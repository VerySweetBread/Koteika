from time import time

import typing
import discord
import schedule

from os     import remove
from bot    import db
from loguru import logger
from random import randint as rint
from discord                import app_commands
from discord.ext            import commands, tasks
from discord.app_commands   import Choice
from discord.app_commands   import TranslationContextLocation as trans_loc
from datetime   import datetime
from matplotlib import ticker
from matplotlib import pyplot as plt
from cogs.emojis    import chocolate

class Economic(commands.Cog, name="Экономика"):
    def __init__(self, bot):
        self.bot = bot

        plt.style.use(['default', "dark.mplstyle"])

    
    def time_translation(self, secs):
        def two_digit(number):
            if len(str(number)) == 1:
                return '0'+str(number)
            return number

        time = f"{secs}s "
        if 60 <= secs < 60*60:
            time = f"{secs//60}:{two_digit(secs%60)}"
        elif 60*60 <= secs < 24*60*60:
            time = f"{secs//60//60}:{two_digit(secs//60%60)}:{two_digit(secs%60)}"
        elif 24*60*60 <= secs:
            time = f"{secs//60//60//24}d {two_digit(secs//60//60%24)}:{two_digit(secs//60%60)}:{two_digit(secs%60)}"
        return time

    def exp_translation(self, exp):
        if exp < 1000:
            return exp
        if exp < 1000000:
            exp /= 1000
            if exp.is_integer():
                return str(int(exp))+'k'
            return "%.1fk" % exp

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.guild is not None and not message.content.startswith(tuple(await self.bot.command_prefix(self.bot, message))):
            data = db.members.find_one({"id": message.author.id})
            flood_channels = db.guild_settings.find_one({"id": message.guild.id})
            if flood_channels is None:
                flood_channels = []
            else:
                flood_channels = flood_channels['flood_channels']

            if time() - 3 >= data["last_mess_time"] and message.channel.id not in flood_channels:
                delta_exp = len(message.content) + len(message.attachments)*100

                db.history.update_one(
                    {'type': 'server', 'id': message.guild.id},
                    {'$inc': {f'current.{datetime.now().hour}': delta_exp}}
                )

                if message.author.voice is not None:
                    delta_exp //= 10
                delta_money = rint(1, 5)

                # Глобальные опыт/уроень
                db.members.update_one({"id": message.author.id},
                                      {"$inc": {"exp": delta_exp}})  # Изменяем exp
                data = db.members.find_one({"id": message.author.id})
                if data is not None:
                    level = data["level"]
                    if level ** 2 * 50 + 5 <= data["exp"]:
                        db.members.update_one({"id": message.author.id},
                                              {"$inc": {"level": 1}})  # Изменяем level
                        if data["level"]+1 >= data["max_level"]:
                            db.members.update_one({"id": message.author.id},
                                                  {"$inc": {"money": (level + 1) * delta_money}})  # Изменяем money


                # Локальные опыт/уровень
                prefix = f"guild_stat.{message.guild.id}"
                if str(message.guild.id) not in db.members.find_one({"id": message.author.id})["guild_stat"].keys():
                    db.members.update_many({"id": message.author.id},
                                           {"$set": {
                                               f"{prefix}.exp": 0,
                                               f"{prefix}.level": 0,
                                               f"{prefix}.secs_in_voice": 0,
                                               f"{prefix}.history": {
                                                    "hour":     {},
                                                    "day":      {},
                                                    "siv_h":    {},
                                                    "siv_d":    {}
                                                }
                                            }})  # Создаем в guild_stat поле для сервера

                data = db.members.find_one({"id": message.author.id})["guild_stat"][str(message.guild.id)]
                db.members.update_one({"id": message.author.id},
                                      {"$inc": {f"{prefix}.exp": delta_exp}})
                data = db.members.find_one({"id": message.author.id})["guild_stat"][str(message.guild.id)]
                level = data["level"]
                if level ** 2 * 50 + 5 <= data["exp"]:
                    db.members.update_one({"id": message.author.id},
                                          {"$inc": {f"{prefix}.level": 1}})
                    data = db.guild_settings.find_one({"id": message.guild.id})
                    if data is not None and data['levelup'] == "send":
                        await message.reply(
                            embed=discord.Embed(
                                title="LEVEL UP", 
                                description=f"{message.author.mention} достиг {level+1} уровня!"
                            ), 
                            delete_after=10, 
                            mention_author=False
                        )

            db.members.update_one({"id": message.author.id}, {"$set": {"last_mess_time": time()}})


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            # При входе
            if before.channel is None:
                humans = list(filter(lambda x: not x.bot, after.channel.members))

                #logger.info(f"{member.name}#{member.discriminator} зашел. В канале теперь {len(humans)} человек")
                
                if len(humans) == 1: pass
                elif len(humans) == 2:
                    self.bot.voice_counter[str(humans[0].id)] = datetime.now()
                    self.bot.voice_counter[str(humans[1].id)] = datetime.now()   
                else:
                    self.bot.voice_counter[str(member.id)] = datetime.now()

            else:
                humans = list(filter(lambda x: not x.bot, before.channel.members))
                if len(humans) == 1:
                    self.voice_register(humans[0], before)
                if len(humans) != 0:
                    self.voice_register(member, before)

            # При выходе
            if after.channel is None:
                try: del self.bot.voice_counter[str(member.id)]
                except: pass


    def voice_register(self, member, voice_state):
        if member.id in self.bot.voice_counter.keys(): 
            secs = (datetime.now() - self.bot.voice_counter[member.id]).seconds
        else: 
            secs = 0

        # TODO: Убрать нахуй эти ифы
        if voice_state.self_deaf:
            k = 0
        elif voice_state.self_mute:
            k = .5
        else:
            k = 1
        if voice_state.self_deaf and (voice_state.self_stream or voice_state.self_video):
            k = 0.1
        elif voice_state.self_stream or voice_state.self_video:
            k *= 2
        exp = int(secs // 5 * k)
        money = exp * rint(1, 5)
        db.members.update_one({"id": member.id}, {
            "$inc": {
                f"guild_stat.{member.guild.id}.secs_in_voice": secs,
                f"guild_stat.{member.guild.id}.exp": exp,
                "exp": exp,
                "money": money
            }})

        db.history.update_one(
            {'type': 'server', 'id': member.guild.id},
            {"$inc": {f'current.{datetime.now().hour}': exp}}
        )

        self.bot.voice_counter[member.id] = datetime.now()

        logger.info(
            f"{member.name}#{member.discriminator}\n"
            f"\tСекунд: +{secs}\n"
            f"\tОпыт:   +{exp}\n"
            f"\tДенег:  +{money}"
        )


    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_data = db.members.find_one({"id": member.id})

        if member_data is None:
            logger.warning("Пользователь не найден")
            return
        
        if str(member.guild.id) in member_data["guild_stat"].keys():
            logger.debug(member_data["guild_stat"][str(member.guild.id)]["exp"], end="\t")
            db.members.update_one(
                {"id": member.id},
                {"$inc": {"exp": member_data["guild_stat"][str(member.guild.id)]["exp"]}}
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_data = db.members.find_one({"id": member.id})

        if member_data is None:
            logger.warning("Пользователь не найден")
            return
        if str(member.guild.id) in member_data["guild_stat"].keys():
            logger.debug(member_data["guild_stat"][str(member.guild.id)]["exp"], end="\t")
            db.members.update_one(
                {"id": member.id},
                {"$dec": {"exp": member_data["guild_stat"][str(member.guild.id)]["exp"]}
            })

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for m in db.members.find({f"guild_stat.{guild.id}": {"$exists": True}}):
            logger.debug(m["guild_stat"][str(guild.id)]["exp"], end="\t")
            db.members.update_one(
                {"id": m['id']},
                {"$inc": {"exp": m["guild_stat"][str(guild.id)]["exp"]}
            })
            logger.debug(m["guild_stat"][str(guild.id)]["exp"])

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        for m in db.members.find({f"guild_stat.{guild.id}": {"$exists": True}}):
            logger.debug(m["guild_stat"][str(guild.id)]["exp"], end="\t")
            db.members.update_one(
                {"id": m['id']},
                {"$dec": {"exp": m["guild_stat"][str(guild.id)]["exp"]}
            })
            logger.debug(m["guild_stat"][str(guild.id)]["exp"])

    async def get_text(self, inter, location, string):
        data = await self.bot.tree.translator.translate(
            app_commands.locale_str(string),
            inter.locale,
            app_commands.TranslationContext(
                trans_loc.other,
                location
            )
        )

        if data is None: return string
        return data

    @app_commands.command(description="View balance and level")
    async def rank(self, inter: discord.Interaction, user: discord.Member = None):
        if user is None: user = inter.user

        if self.bot.get_user(user.id).bot:
            await inter.response.send_message(await self.get_text(inter, "rank", "Bot hasn't experience"))
            return

        user_data = db.members.find_one({"id": user.id})
        if user_data is None or str(inter.guild.id) not in user_data['guild_stat'].keys():
            await inter.response.send_message("Об этом пользователе информации пока нет")
            return

        if str(user.id) in self.bot.voice_counter.keys():
            prefix = f"guild_stat.{inter.guild.id}"
            if str(inter.guild.id) not in user_data["guild_stat"].keys():
                db.members.update_many(
                    {"id": user.id},
                    {"$set": {
                        f"{prefix}.exp": 0,
                        f"{prefix}.level": 0,
                        f"{prefix}.secs_in_voice": 0,
                        f"{prefix}.history": {
                            "hour": {},
                            "day": {}
                        }
                    }}
                )  # Создаем в guild_stat поле для сервера

            self.voice_register(user, user.voice)

            user_data = db.members.find_one({"id": user.id})
            if user_data is None: return

        if inter.guild is not None:
            color = inter.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        history = user_data['history']
        if len(history['hour']) >= 1:
            per_hour = user_data['exp'] - history['hour'][list(history['hour'].keys())[-1]]
        else: per_hour = "???"
        if len(history['hour']) >= 2:
            last_hour = history['hour'][list(history['hour'].keys())[-1]] - history['hour'][list(history['hour'].keys())[-2]]
        else: last_hour = "???"

        if len(history['day']) >= 1:
            per_day = user_data['exp'] - history['day'][list(history['day'].keys())[-1]]
        else: per_day = "???"
        if len(history['day']) >= 2:
            last_day = history['day'][list(history['day'].keys())[-1]] - history['day'][list(history['day'].keys())[-2]]
        else: last_day = "???"


        description = f"{await self.get_text(inter, 'rank', 'Money')}: {user_data['money']}{chocolate}\n\n" \
                      f"__{await self.get_text(inter, 'rank', 'Global stats')}:__\n" \
                      f"{await self.get_text(inter, 'rank', 'Level')}: {user_data['level']}\n" \
                      f"{await self.get_text(inter, 'rank', 'Exp')}: {user_data['exp']} / {user_data['level'] ** 2 * 50 + 5}" \
                      f" ({(user_data['level'] ** 2 * 50 + 5) - user_data['exp']})\n" \
                      f"{await self.get_text(inter, 'rank', 'Per hour')}: {per_hour}, {await self.get_text(inter, 'rank', 'per the past hour')}: {last_hour}\n" \
                      f"{await self.get_text(inter, 'rank', 'Per day')}: {per_day}, {await self.get_text(inter, 'rank', 'per the past day')}: {last_day}\n"
          
        secs = user_data['guild_stat'][str(inter.guild.id)]['secs_in_voice']

        if "guild_stat" in list(user_data.keys()):
            if inter.guild is not None and str(inter.guild.id) in list(user_data['guild_stat'].keys()):
                description += f"\n__{await self.get_text(inter, 'rank', 'On this guild')}:__\n" \
                               f"{await self.get_text(inter, 'rank', 'Level')}: {user_data['guild_stat'][str(inter.guild.id)]['level']}\n" \
                               f"{await self.get_text(inter, 'rank', 'Exp')}: {user_data['guild_stat'][str(inter.guild.id)]['exp']} / " \
                               f"{user_data['guild_stat'][str(inter.guild.id)]['level'] ** 2 * 50 + 5}" \
                               f" ({(user_data['guild_stat'][str(inter.guild.id)]['level'] ** 2 * 50 + 5) - user_data['guild_stat'][str(inter.guild.id)]['exp']})\n" \
                               f"{await self.get_text(inter, 'rank', 'Time in voice channels')}: {self.time_translation(secs)}"


        e = discord.Embed(title=f"{await self.get_text(inter, 'rank', 'Info about')} {self.bot.get_user(user.id).name}",
                          description=description,
                          color=color)
        await inter.response.send_message(embed=e)

    @app_commands.command(description="Top members of the guild")
    @app_commands.describe(category='Category')
    @app_commands.choices(category=[
        Choice(name='Balance',                  value="Баланс"),
        Choice(name='Experience',               value="Опыт"),
        Choice(name='Time in voice channel',    value="Время в войсе")
    ])
    # @logger.catch
    async def top(self, inter: discord.Interaction, category: Choice[str] = None):
        if category is None   :
            category = "Опыт"
        else:
            category = category.value
        categories = {
                    'Уровень':          f"guild_stat.{inter.guild.id}.level", 
                    'Баланс':           "money", 
                    'Опыт':             f"guild_stat.{inter.guild.id}.exp", 
                    'Время в войсе':    f"guild_stat.{inter.guild.id}.secs_in_voice"
                }

        if inter.guild is not None:
            color = inter.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        e = discord.Embed(title="Топ", description=category, color=color)
        data_ = list(db.members.find({f"guild_stat.{inter.guild.id}": {"$exists": True}}).sort(categories[category], -1))[:10]

        if len(data_) == 0:
            await inter.response.send_message("Недостаточно данных! Попробуйте завтра")
            return

        l = min(len(data_), 10)

        MAX_COLONS = 25

        if category == "Опыт":
            max_val = data_[0]["guild_stat"][str(inter.guild.id)]["exp"]
        elif category == "Время в войсе":
            max_val = data_[0]['guild_stat'][str(inter.guild.id)]['secs_in_voice']
        elif category == "Баланс":
            max_val = data_[0]['money']

        for place in range(l):
            m = data_[place]
            if 'level' not in m['guild_stat'][str(inter.guild.id)].keys():
                db.members.update_one(
                    {'id': m['id']},
                    {'$set': {f'guild_stat.{inter.guild.id}.level': 0}}
                )
                m['guild_stat'][str(inter.guild.id)]['level'] = 0

            data = {"Уровень":          ["Ур:",         m['guild_stat'][str(inter.guild.id)]['level']], 
                    "Опыт":             ["Опыт:",       self.exp_translation(m['guild_stat'][str(inter.guild.id)]["exp"]),              m['guild_stat'][str(inter.guild.id)]["exp"]], 
                    "Время в войсе":    [":sound:",     self.time_translation(m['guild_stat'][str(inter.guild.id)]['secs_in_voice']),   m['guild_stat'][str(inter.guild.id)]['secs_in_voice']],  
                    "Баланс":           [":moneybag:",  m["money"],                                                                     m["money"]]
                    }
            u = self.bot.get_user(m['id'])
            if u is None:
                name = str(place + 1) + '. ' + m["name"]
            else:
                name = str(place + 1) + '. ' + u.name + '#' + str(u.discriminator)

            e.add_field(name=name,
                        inline=False,
                        value=f"{data[category][0]} {data[category][1]} | " +
                              " | ".join([f"{data[k][0]} {data[k][1]}" for k in data.keys() if k != category]) + 
                              "\n" + str(int(data[category][2]/max_val*100)) + '% '+  
                              "█" * int(data[category][2]/max_val*MAX_COLONS) +
                              "▌" * int((data[category][2]/max_val*MAX_COLONS)%2))

        await inter.response.send_message(embed=e)

    @app_commands.command(description="Comparison of exp with other members")
    @app_commands.choices(period=[
        Choice(name='Per the entire period',    value=-1),
        Choice(name='Per month',                value=24*30),
        Choice(name='Per week',                 value=24*7),
        Choice(name='Per day',                  value=24)
    ])
    async def dif_graph(self, inter: discord.Interaction, user1: discord.Member, user2: discord.Member = None, period: Choice[int] = -1):
        if period != -1: period = period.value

        ts = datetime.now().timestamp()

        # if user1 is None: user1 = user2
        user1 = user1.id
        if user2 is None:
            user2 = inter.user.id
        else:
            user2 = user2.id

        if self.bot.get_user(user1).bot or self.bot.get_user(user2).bot:
            await inter.response.send_message("У ботов нет опыта. Они всемогущи")
            return


        db_ = db.members
        info1 = db_.find_one({"id": user1})['guild_stat'][str(inter.guild.id)]['history']['hour']
        info2 = db_.find_one({"id": user2})['guild_stat'][str(inter.guild.id)]['history']['hour']
        info1[str(int(ts))] = db_.find_one({"id": user1})['guild_stat'][str(inter.guild.id)]['exp']
        info2[str(int(ts))] = db_.find_one({"id": user2})['guild_stat'][str(inter.guild.id)]['exp']
        

        if period == -1:
            data1 = list(info1.values()) 
            data2 = list(info2.values()) 
        else:
            data1 = [info1[key] for key in info1.keys() if int(key) >= ts-period*60*60]
            data2 = [info2[key] for key in info2.keys() if int(key) >= ts-period*60*60]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(list(map(int, info1.keys()))[-len(data1):], data1, marker='.', label=self.bot.get_user(user1).name)
        ax.plot(list(map(int, info2.keys()))[-len(data2):], data2, marker='.', label=self.bot.get_user(user2).name)
        # ax.plot([i for info1.keys()], data2, label="Разница")
        ax.grid(True)
        ax.set_ylabel('Опыт')
        ax.set_xlabel('Время (ч)')
        ax.legend(loc='upper left')

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))

        if period == 24:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*5, offset=0))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%Hh')))
        elif period == 24*7:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24, offset=0))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
        else:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24*7, offset=0))
            ax.xaxis.set_minor_locator(ticker.IndexLocator(base=60*60*24, offset=0))
            ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d')))


        ax.legend().get_frame().set_boxstyle('Round', pad=0.2, rounding_size=1)
        ax.legend().get_frame().set_linewidth(0.0)
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_color('#303030')
        ax.spines['right'].set_color('#303030')

        fig.savefig(f'tmp/{inter.id}.png')
        with open(f'tmp/{inter.id}.png', 'rb') as f:
            await inter.response.send_message(file=discord.File(f))
        remove(f'tmp/{inter.id}.png')


    @app_commands.command()
    @app_commands.choices(period=[
        Choice(name='Per the entire period',    value=-1),
        Choice(name='Per month',                value=24*30),
        Choice(name='Per week',                 value=24*7),
        Choice(name='Per day',                  value=24)
    ])
    async def top_graph(self, inter: discord.Interaction, period: Choice[int]=-1):
        if period != -1: period = period.value

        ts = datetime.now().timestamp()

        db_mem = db.members
        data = list(db_mem.find({f"guild_stat.{inter.guild.id}": {"$exists": True}}).sort(f"guild_stat.{inter.guild.id}.exp", -1))[:10]

        if not data:
            await inter.response.send_message("Недостаточно данных. Попробуйте завтра")
            return

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.grid(True)
        ax.set_ylabel('Опыт', color=(1., 1., 1.))
        ax.set_xlabel('Время', color=(1., 1., 1.))
        # ax.set_facecolor((.12, .12, .12))
        marker = '.' if -1 < period <= 24 else ''

        for user in data:
            info = user['guild_stat'][str(inter.guild.id)]['history']['hour']

            if period == -1:
                vals = list(info.values())
            else:
                vals = [info[key] for key in info.keys() if int(key) >= ts-period*60**2]

            ax.plot(list(map(int, info.keys()))[-len(vals):], vals, marker=marker, label=self.bot.get_user(user['id']).name)
        
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))

        if period == 24:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*5, offset=0))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%Hh')))
        elif period == 24*7:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24, offset=0))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
        else:
            ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24*7, offset=0))
            ax.xaxis.set_minor_locator(ticker.IndexLocator(base=60*60*24, offset=0))
            ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d')))
            
            # fig.autofmt_xdate()

        ax.legend().get_frame().set_boxstyle('Round', pad=.2, rounding_size=1)
        ax.legend().get_frame().set_linewidth(.0)
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible('#303030')
        ax.spines['right'].set_visible('#303030')

        fig.savefig(f'tmp/{inter.id}.png')
        with open(f'tmp/{inter.id}.png', 'rb') as f:
            await inter.response.send_message(file=discord.File(f))
        remove(f'tmp/{inter.id}.png')

# @logger.catch
async def setup(bot):
    await bot.add_cog(Economic(bot))

