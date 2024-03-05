from utils.translate import get_text

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
from datetime   import datetime
from matplotlib import ticker
from matplotlib import pyplot as plt
from utils.emojis    import chocolate

class Economic(commands.Cog, name="Экономика"):
    def __init__(self, bot):
        self.bot = bot

        db.cursor().execute("CREATE TABLE IF NOT EXISTS economics (\n"
                            "    user_id INTEGER NOT NULL         ,\n"
                            "    guild_id INTEGER                 ,\n"
                            "    exp REAL                         ,\n"
                            # "    money INTEGER                    ,\n"
                            "    last_message_time TIMESTAMP      ,\n"
                            "    time_in_voice_channels            \n"
                            ")                                     ")
        db.commit()

        plt.style.use(['default', "dark.mplstyle"])

    
    def time_translation(self, secs: int) -> str:
        if secs < 60:
            return f"{secs}s "
        if 60 <= secs < 60*60:
            return f"{secs//60}:{secs%60:0>2}"
        elif 60*60 <= secs < 24*60*60:
            return f"{secs//60//60}:{secs//60%60:0>2}:{secs%60:0>2}"
        elif 24*60*60 <= secs:
            return f"{secs//60//60//24}d {secs//60//60%24:0>2}:{secs//60%60:0>2}:{secs%600>2}"

    def exp_translation(self, exp: float) -> str:
        if exp < 1000:
            return str(int(exp))
        if exp < 1000000:
            exp /= 1000
            if exp.is_integer():
                return f'{int(exp)}k'
            return f'{exp:.1f}k'
        exp /= 10**6
        if exp.is_integer():
            return f'{int(exp)}M'
        return f'{exp:.1f}M'

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.guild:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM economics WHERE user_id = ? AND guild_id = ?", (message.author.id, message.guild.id))
            data = cursor.fetchone()

            if not data:
                data = (message.author.id, message.guild.id, 0, datetime.now(), 0)
                cursor.execute("INSERT INTO economics VALUES (?, ?, ?, ?, ?)", data)

            # data = await db.members.find_one({"id": message.author.id})
            # flood_channels = await db.guild_settings.find_one({"id": message.guild.id, 'type': 'general'})
            # if flood_channels is None:
            #     flood_channels = []
            # else:
            #     flood_channels = flood_channels['flood_channels']
            # cursor.execute("SELECT channel_id FROM flood_channels WHERE guild_id = ?", (message.guild.id,))  # TODO
            logger.debug(cursor.fetchall())
            flood_channels = []  # TODO

            if time() - 3 >= data[3].timestamp() and message.channel.id not in flood_channels:
                delta_exp = len(message.content) + len(message.attachments)*100

                if message.author.voice:
                    delta_exp //= 10
                delta_money = rint(1, 5)

                cursor.execute("UPDATE economics SET exp = exp + ? WHERE user_id = ? AND guild_id = ?", (delta_exp, message.author.id, message.guild.id))


            cursor.execute("UPDATE economics SET last_message_time = ? WHERE user_id = ? AND guild_id = ?", (datetime.now(), message.author.id, message.guild.id))
            db.commit()


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            # При входе
            if before.channel is None:
                humans = list(filter(lambda x: not x.bot, after.channel.members))
                
                if len(humans) == 1: pass
                elif len(humans) == 2:
                    self.bot.voice_counter[str(humans[0].id)] = datetime.now()
                    self.bot.voice_counter[str(humans[1].id)] = datetime.now()   
                else:
                    self.bot.voice_counter[str(member.id)] = datetime.now()

            else:
                humans = list(filter(lambda x: not x.bot, before.channel.members))
                if len(humans) == 1:
                    await self.voice_register(humans[0], before)
                if len(humans) != 0:
                    await self.voice_register(member, before)

            # При выходе
            if after.channel is None:
                try: del self.bot.voice_counter[str(member.id)]
                except: pass


    async def voice_register(self, member, voice_state):
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
        if voice_state.self_stream or voice_state.self_video:
            k *= 2
        exp = secs / 5 * k
        cursor = db.cursor()
        logger.debug((member.id, member.guild.id))
        cursor.execute("SELECT * FROM economics WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id))
        if cursor.fetchone():
            cursor.execute("UPDATE economics SET time_in_voice_channels = time_in_voice_channels + ?, exp = exp + ? WHERE user_id = ? AND guild_id = ?", (secs, exp, member.id, member.guild.id))
        else:
            cursor.execute("INSERT INTO economics VALUES (?, ?, ?, ?, ?)", (member.id, member.guild.id, exp, datetime.fromtimestamp(0), secs))

        # await db.history.update_one(
        #     {'type': 'server', 'id': member.guild.id},
        #     {"$inc": {f'current.{datetime.now().hour}': exp}}
        # )
        # cursor.execute("UPDATE history SET time = ", (time.strftime("%y.%m.%d-%H")))  # TODO

        self.bot.voice_counter[member.id] = datetime.now()

        # logger.info(
        #     f"{member.name}#{member.discriminator}\n"
        #     f"\tСекунд: +{secs}\n"
        #     f"\tОпыт:   +{exp}\n"
        #     f"\tДенег:  +{money}"
        # )
        db.commit()


    stat_gr = app_commands.Group(name="statistics", description="Some statistics")

    @stat_gr.command(description="View balance and level")
    async def rank(self, inter: discord.Interaction, user: discord.Member = None):
        if user is None: user = inter.user

        if self.bot.get_user(user.id).bot:
            await inter.response.send_message(await get_text(inter, "Bot hasn't experience", "rank"))
            return

        if str(user.id) in self.bot.voice_counter.keys():
            self.voice_register(user, user.voice)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM economics WHERE user_id = ? AND guild_id = ?", (user.id, inter.guild.id))
        user_data = cursor.fetchone()
        if not user_data:
            await inter.response.send_message(await get_text(inter, "no_user_info", 'rank'))
            return

        if inter.guild is not None:
            color = inter.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        e = discord.Embed(title=f"{await get_text(inter, 'Info about', 'rank')} {self.bot.get_user(user.id).name}",
                          description=f"{await get_text(inter, 'Experience', 'rank')}: {int(user_data[2])}",
                          color=color)
        await inter.response.send_message(embed=e)

    @stat_gr.command(description="Top members of the guild")
    @app_commands.describe(category='Category')
    @app_commands.choices(category=[
        Choice(name='Experience',               value="exp"),
        Choice(name='Time in voice channel',    value="time_in_voice_channels")
    ])
    async def top(self, inter: discord.Interaction, category: Choice[str] = None):
        if category is None   :
            category = "exp"
        else:
            category = category.value

        color = inter.guild.me.color
        if color == discord.Color.default():
            color = discord.Color(0xaaffaa)
        e = discord.Embed(title="Топ", description=category, color=color)
        cursor = db.cursor()
        cursor.execute("SELECT user_id, exp, time_in_voice_channels FROM economics WHERE guild_id = ? ORDER BY ?", (inter.guild.id, category))
        data = cursor.fetchmany(10)

        if not data:
            await inter.response.send_message(await get_text(inter, "Not enough data. Try later", "rank"))
            return

        for user in data:
            e.add_field(
                name=self.bot.get_user(user[0]),
                inline=False,
                value=f"{await get_text(inter, 'Exp', 'rank')}: {int(user[1])}\nVoice: {self.time_translation(user[2])}"  # TODO
            )

        await inter.response.send_message(embed=e)

    # @stat_gr.command(description="Comparison of exp with other members")
    # @app_commands.choices(period=[
    #     Choice(name='Per the entire period',    value=-1),
    #     Choice(name='Per month',                value=24*30),
    #     Choice(name='Per week',                 value=24*7),
    #     Choice(name='Per day',                  value=24)
    # ])
    # async def dif_graph(self, inter: discord.Interaction, user1: discord.Member, user2: discord.Member = None, period: Choice[int] = -1):
    #     if period != -1: period = period.value
    #
    #     ts = datetime.now().timestamp()
    #
    #     user1 = user1.id
    #     if user2 is None:
    #         user2 = inter.user.id
    #     else:
    #         user2 = user2.id
    #
    #     if self.bot.get_user(user1).bot or self.bot.get_user(user2).bot:
    #         await inter.response.send_message("У ботов нет опыта. Они всемогущи")  # TODO: translate
    #         return
    #
    #
    #     db_ = db.members
    #     info1 = await db_.find_one({"id": user1})['guild_stat'][str(inter.guild.id)]['history']['hour']
    #     info2 = await db_.find_one({"id": user2})['guild_stat'][str(inter.guild.id)]['history']['hour']
    #     info1[str(int(ts))] = await db_.find_one({"id": user1})['guild_stat'][str(inter.guild.id)]['exp']
    #     info2[str(int(ts))] = await db_.find_one({"id": user2})['guild_stat'][str(inter.guild.id)]['exp']
    #     
    #
    #     if period == -1:
    #         data1 = list(info1.values()) 
    #         data2 = list(info2.values()) 
    #     else:
    #         data1 = [info1[key] for key in info1.keys() if int(key) >= ts-period*60*60]
    #         data2 = [info2[key] for key in info2.keys() if int(key) >= ts-period*60*60]
    #
    #     fig, ax = plt.subplots(figsize=(8, 5))
    #     ax.plot(list(map(int, info1.keys()))[-len(data1):], data1, marker='.', label=self.bot.get_user(user1).name)
    #     ax.plot(list(map(int, info2.keys()))[-len(data2):], data2, marker='.', label=self.bot.get_user(user2).name)
    #     # ax.plot([i for info1.keys()], data2, label="Разница")
    #     ax.grid(True)
    #     ax.set_ylabel('Опыт')  # TODO: translate
    #     ax.set_xlabel('Время (ч)')
    #     ax.legend(loc='upper left')
    #
    #     ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
    #
    #     if period == 24:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*5, offset=0))
    #         ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%Hh')))
    #     elif period == 24*7:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24, offset=0))
    #         ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
    #     else:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24*7, offset=0))
    #         ax.xaxis.set_minor_locator(ticker.IndexLocator(base=60*60*24, offset=0))
    #         ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d')))
    #
    #
    #     ax.legend().get_frame().set_boxstyle('Round', pad=0.2, rounding_size=1)
    #     ax.legend().get_frame().set_linewidth(0.0)
    #     ax.xaxis.set_ticks_position('none')
    #     ax.yaxis.set_ticks_position('none')
    #
    #     ax.spines['bottom'].set_visible(False)
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['left'].set_color('#303030')
    #     ax.spines['right'].set_color('#303030')
    #
    #     fig.savefig(f'tmp/{inter.id}.png')
    #     with open(f'tmp/{inter.id}.png', 'rb') as f:
    #         await inter.response.send_message(file=discord.File(f))
    #     remove(f'tmp/{inter.id}.png')
    #
    # @stat_gr.command()
    # @app_commands.choices(period=[
    #     Choice(name='Per the entire period',    value=-1),
    #     Choice(name='Per month',                value=24*30),
    #     Choice(name='Per week',                 value=24*7),
    #     Choice(name='Per day',                  value=24)
    # ])
    # async def top_graph(self, inter: discord.Interaction, period: Choice[int]=-1):
    #     if period != -1: period = period.value
    #
    #     ts = datetime.now().timestamp()
    #
    #     db_mem = db.members
    #     data = await db_mem.find({f"guild_stat.{inter.guild.id}": {"$exists": True}}).sort(f"guild_stat.{inter.guild.id}.exp", -1).to_list(10)
    #
    #     if not data:
    #         await inter.response.send_message("Недостаточно данных. Попробуйте завтра")
    #         return
    #
    #     fig, ax = plt.subplots(figsize=(8, 5))
    #     ax.grid(True)
    #     ax.set_ylabel('Опыт', color=(1., 1., 1.))
    #     ax.set_xlabel('Время', color=(1., 1., 1.))
    #     # ax.set_facecolor((.12, .12, .12))
    #     marker = '.' if -1 < period <= 24 else ''
    #
    #     for user in data:
    #         info = user['guild_stat'][str(inter.guild.id)]['history']['hour']
    #
    #         if period == -1:
    #             vals = list(info.values())
    #         else:
    #             vals = [info[key] for key in info.keys() if int(key) >= ts-period*60**2]
    #
    #         if not vals: continue
    #
    #         ax.plot(list(map(int, info.keys()))[-len(vals):], vals, marker=marker, label=self.bot.get_user(user['id']).name)
    #     
    #     ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
    #
    #     if period == 24:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*5, offset=0))
    #         ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%Hh')))
    #     elif period == 24*7:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24, offset=0))
    #         ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d.%m')))
    #     else:
    #         ax.xaxis.set_major_locator(ticker.IndexLocator(base=60*60*24*7, offset=0))
    #         ax.xaxis.set_minor_locator(ticker.IndexLocator(base=60*60*24, offset=0))
    #         ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: datetime.fromtimestamp(x).strftime('%d')))
    #         
    #         # fig.autofmt_xdate()
    #
    #     ax.legend().get_frame().set_boxstyle('Round', pad=.2, rounding_size=1)
    #     ax.legend().get_frame().set_linewidth(.0)
    #     ax.xaxis.set_ticks_position('none')
    #     ax.yaxis.set_ticks_position('none')
    #
    #     ax.spines['bottom'].set_visible(False)
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['left'].set_visible('#303030')
    #     ax.spines['right'].set_visible('#303030')
    #
    #     fig.savefig(f'tmp/{inter.id}.png')
    #     with open(f'tmp/{inter.id}.png', 'rb') as f:
    #         await inter.response.send_message(file=discord.File(f))
    #     remove(f'tmp/{inter.id}.png')

# @logger.catch
async def setup(bot):
    await bot.add_cog(Economic(bot))

