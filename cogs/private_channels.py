import discord
from discord.ext import commands
from discord.utils import get

from cogs.checks import is_white
import asyncio
from cogs.emojis import check_mark

from bot import db


class privateChannels(commands.Cog, name="Приватные комнаты"):
    """Работа с приватными комнатами"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        for chan in [i["id"] for i in db.private_channels.find()]:
            if not self.bot.get_channel(chan):
                db.private_channels.delete_one({"id": chan})

        v_channels = [i["id"] for i in db.private_channels.find()]
        v_categories = [self.bot.get_channel(i).category_id for i in v_channels]

        if (
                before.channel is not None and
                len(before.channel.members) == 0 and
                before.channel.id not in v_channels and
                before.channel.category_id in v_categories
        ):
            await before.channel.delete()

        if after.channel is not None and after.channel.id in v_channels:
            #, overwrites={
            #    member: discord.PermissionOverwrite(manage_channels=True,
            #                                        move_members=True,
            #                                        manage_permissions=True)
            #}

            new_private = await after.channel.category.create_voice_channel(name=member.display_name)

            try:
                await member.edit(voice_channel=new_private)
            except discord.errors.HTTPException:
                await new_private.delete()

            try:
                await new_private.set_permissions(member, manage_channels=True, move_members=True, manage_permissions=True)
            except:
                pass

        try:
            voice = before.channel.guild.me.voice
        except:
            voice = after.channel.guild.me.voice

        if voice:
            if len(voice.channel.members) == 1:
                await member.guild.voice_client.disconnect()

    @commands.command(brief="Присваивает комнату главной",
                      help="Идея приватных комнат состоит в том, что при входе в ГК создается пприватная комната. "
                           "Тот самый ГК и является главной комнатой. Эта команда присваивает ГК, в котором вы "
                           "находитесь в главный")
    @commands.check(is_white)
    async def set_private(self, ctx):
        if ctx.author.voice.channel.id in [i["id"] for i in db.private_channels.find()]:
            await ctx.message.delete()
            message = await ctx.send('Канал уже добавлен')
        else:
            db.private_channels.insert_one({"id": ctx.author.voice.channel.id})
            await ctx.message.add_reaction(check_mark)
            message = ctx.message

        await asyncio.sleep(3)
        await message.delete()

    @commands.command(brief="Делает комнату не приватной")
    @commands.check(is_white)
    async def unset_private(self, ctx):
        if ctx.author.voice is not None:
            message = await ctx.send("Требуется выйти из ГК")
            await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
                member == ctx.message.author and after.channel is None)
            await message.edit(content="Зайдите в ГК")
            await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
                member == ctx.message.author and after.channel is not None)
        else:
            message = await ctx.send("Зайдите в ГК")
            await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
                member == ctx.message.author and after.channel is not None)
        if ctx.author.voice.channel.id in [i["id"] for i in db.private_channels.find()]:
            db.private_channels.delete_one({"id": ctx.author.voice.channel.id})
            await ctx.message.add_reaction(check_mark)
        else:
            await message.edit(content='Этот канал не является приватным')

        await asyncio.sleep(3)
        await ctx.message.delete()
        await message.delete()


async def setup(bot):
    await bot.add_cog(privateChannels(bot))
