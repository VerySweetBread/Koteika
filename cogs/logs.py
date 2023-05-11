from datetime import datetime

import discord
from discord.ext import commands
from datetime import timedelta

from cogs.translate import *
from bot import db


class Logs(commands.Cog, name="Логи"):
    """Настройка логов сервера"""

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(brief="Управление логами", help="В РАЗРАБОТКЕ")
    async def logs(self, ctx):
        color = ctx.guild.me.color
        if color == discord.Color.default():
            color = discord.Color(0xaaffaa)

        info = db.logs.find({"type": "log_chat", "guild": ctx.guild.id})
        e = discord.Embed(title="Логи сервера", color=color)
        for i in info:
            channel = self.bot.get_channel(i["channel"])
            listening = [f"`{j}`" for j in i["listen"]]
            if len(listening) >= 3:
                listening = listening[:2] + [str(len(listening) - 2)]
            e.add_field(name=channel.mention, value=', '.join(listening))
        message = await ctx.send(embed=e)
        await message.add_reaction("➕")

        def check(reaction, user):
            return reaction.message == message and str(reaction.emoji) == "➕" and user == ctx.message.author

        await self.bot.wait_for('reaction_add', check=check)
        await message.edit(content="Выбирите канал", embed=None)
        await message.clear_reactions()

        def check(mes):
            if mes.author == ctx.author:
                if mes.channel_mentions:
                    return mes.channel_mentions[0]
                else:
                    return mes.content.isnumeric()

        mes = await self.bot.wait_for('message', check=check)
        if mes.channel_mentions:
            channel = mes.channel_mentions[0]
        else:
            channel = self.bot.get_channel(mes.content)
        await ctx.send("Done")

        e = discord.Embed(title="Виберете события:", description=channel.mention)
        await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        e = discord.Embed(title="Ошибка", description=event, color=discord.Color(0xff0000))
        e.add_field(name="args", value=str(args))
        e.add_field(name="kwargs", value=str(kwargs))
        await self.bot.get_channel(795050679776968704).send(embed=e)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        e = discord.Embed(title="Ошибка", color=discord.Color(0xff0000))
        e.add_field(name="error", value=str(error))
        e.add_field(name="Команда", value=ctx.message.content)
        e.add_field(name="Сервер", value=f"{ctx.guild.name} ({ctx.guild.id})")
        await self.bot.get_channel(795050679776968704).send(embed=e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        e = discord.Embed(title=f"Бот зашел на сервер (#{len(self.bot.guilds)})",
                          description=f"Имя: {guild.name}\n" \
                                      f"Владелец: {guild.owner.name}\n" \
                                      f"Создан: {(guild.created_at + timedelta(hours=3)).isoformat()}\n" \
                                      f"Участников: {len(guild.members)}\n" \
                                      f"ID: {guild.id}",
                          color=discord.Color(0x388e3c))
        e.set_thumbnail(url=guild.icon)
        mes = await self.bot.get_channel(795050679776968704).send(embed=e)

        db.logs.insert_one({"type": "guild",
                            "id_guild": guild.id,
                            "id_mes_log": mes.id,
                            "joined_at": guild.me.joined_at})

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        data = db.logs.find_one({"id_guild": guild.id})

        e = discord.Embed(
            title=f"Бот вышел из сервера (#{len(self.bot.guilds)})",
            color=discord.Color(0xd32f2f)
        )

        if data is not None:
            mes_id = data["id_mes_log"]
            joined_at = data["joined_at"]
            was = (datetime.now() - joined_at).total_seconds()
            was -= 3*60*60

            days = int(was / 60 / 60 / 24)
            hours = int(was / 60 / 60 - days * 24)
            minutes = int(was / 60 - (hours * 60 + days * 24 * 60))
            seconds = int(was % 60)

            mes = await self.bot.get_channel(795050679776968704).fetch_message(mes_id)

            e.add_field(name="был на сервере:",
                value=f"Дней: {days}\n"
                      f"Часов: {hours}\n"
                      f"Минут: {minutes}\n"
                      f"Секунд: {seconds}\n")
        e.set_thumbnail(url=guild.icon)

        if data is not None:
            await mes.reply(embed=e)
            db.logs.delete_one({"id_guild": guild.id})

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        info = db.logs.find({"type": "log_chat", "guild": message.guild.id})
        if info:
            for i in info:
                if "message_delete" in i["listen"]:
                    region = region_to_str(message.guild.region)
                    e = discord.Embed(title=translate("$log_messageDelete", region))
                    e.add_field(name=translate("$log_author", region),
                                value="{0.mention} ({0.id})".format(message.author))
                    e.add_field(name=translate("$log_channel", region),
                                value="{0.mention} ({0.id})".format(message.channel))
                    e.add_field(name=translate("$log_text".region), value=message.content)
                    self.bot.get_channel(i["channel"]).send(embed=e)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(1)
        if db.guild.find_one({"id": member.guild.id}) is not None:
            print(2)
            if "default_role" in db.guild.find_one({"id": member.guild.id}).keys():
                print(3)
                await member.add_roles(
                    member.guild.get_role(
                        db.guild.find_one({"id": member.guild.id})["default_role"]
                    )
                )


async def setup(bot):
    await bot.add_cog(Logs(bot))
