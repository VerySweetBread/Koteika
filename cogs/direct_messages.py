import asyncio

import discord
from discord.ext import commands
from typing import Optional

from discord.utils import get

from cogs.emojis import check_mark, XX


class DM(commands.Cog, name="ЛС"):
    """Работа с ЛС"""

    def __init__(self, bot):
        self.bot = bot
        self.last_dm = 459823895256498186


    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) == discord.channel.DMChannel:
            if message.author != message.channel.me and message.author.id != self.bot.owner_id:
                await get(self.bot.users, id=self.bot.owner_id).send(f'```{message.author.name} {message.author.id}'
                                                                     f'```\n' + message.content)
                if message.attachments:
                    await get(self.bot.users, id=self.bot.owner_id).send(str(message.attachments))

                self.last_dm = message.author.id

    @commands.command(brief="Отправляет сообщение",
                      aliases=['send', 'DMsend', 'DM_send'])
    @commands.is_owner()
    async def dm_send(self, ctx, id: Optional[int] = None, *, text: str):
        sended = False
        if id is None: id = self.last_dm

        for guild in self.bot.guilds:
            member = guild.get_member(id)
            if member is not None:
                await member.send(text)
                await ctx.message.add_reaction(check_mark)
                self.last_dm = id
                sended = True
                break
        if not sended:
            await ctx.message.add_reaction(XX)

        await asyncio.sleep(3)
        await ctx.message.delete()

    @commands.command(brief="Удаляет свои сообщения из ЛС",
                      aliases=['delete', 'DMdelete', 'DM_delete', 'dm_del'])
    async def dm_delete(self, ctx, count: int = 100):
        if type(ctx.channel) == discord.channel.DMChannel:
            async for message in ctx.channel.history(limit=count):
                if message.author == message.channel.me:
                    await message.delete()


async def setup(bot):
    await bot.add_cog(DM(bot))
