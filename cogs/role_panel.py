import discord
from discord.ext import commands
from typing import Optional
import re

from bot import db


class Panel(commands.Cog, name="Панель ролей"):
    """Создание и изменение панели для выбора ролей"""
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def add_role_panel(self, ctx):
        emoji_patter = re.compile(r"(<:\w+:(\d+)>)|([^\s\d\w])", flags=re.IGNORECASE)


        def check(mes):
            return mes.author == ctx.author  # len(mes.role_mentions) == 1

        menu = await ctx.send("Для добавления ролей в меню напишите `эмодзи роль`\n"
                       "Для удаления роли из меню напишите порядковый номер в списке\n"
                       "Для подтверждения напишите `.`\n\n"
                       "*Добавлено:*")
        while True:
            mes = await self.bot.wait_for('message', check=check)
            if mes.content == ".":
                break
            elif len(mes.role_mentions) == 1:
                content = mes.content.split()
                result = ""
                if emoji_patter.match(content[0]):
                    result = f"{content[0]} - {content[1]}"
                if content[0] is int:
                    pass


        await ctx.send("Done")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def default_role(self, ctx, role: Optional[discord.Role] = None):
        if role is None:
            data = db.guild.find_one({"id": ctx.guild.id})
            if data is not None:
                if "default_role" in data.keys():
                    await ctx.send(ctx.guild.get_role(data["default_role"]).mention)
                else:
                    await ctx.send("Роли по умолчанию не установлено")
            else:
                await ctx.send("Роли по умолчанию не установлено")
        else:
            if db.guild.find_one({"id": ctx.guild.id}) is not None:
                db.guild.update_one({"id": ctx.guild.id}, {"$set": {"default_role": role.id}})
            else:
                db.guild.insert_one({"id": ctx.guild.id, "default_role": role.id})


async def setup(bot):
    await bot.add_cog(Panel(bot))
