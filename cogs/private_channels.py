import discord
from discord.ext import commands
from discord.utils import get

from utils.checks import is_white
import asyncio
from utils.emojis import check_mark

from bot import db


class privateChannels(commands.Cog, name="Приватные комнаты"):
    """Работа с приватными комнатами"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (
            before.channel and
            (await db.private_channels.find_one({'id': before.channel.id})) and
            not self.bot.get_channel(before.channel.id)
        ):
            await db.private_channels.delete_one({'id': before.channel.id})

        if (
            before.channel and
            len(before.channel.members) == 0 and
            not (await db.private_channels.find_one({'id': before.channel.id})) and
            (await db.private_channels.find_one({'category_id': before.channel.category_id}))
        ):
            await before.channel.delete()

        if after.channel and (await db.private_channels.find_one({"id": after.channel.id})):
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
        if (await db.private_channels.find({'id': ctx.author.voice.channel.id})):
            await ctx.message.delete()
            message = await ctx.send('Канал уже добавлен')
        else:
            await db.private_channels.insert_one({"id": ctx.author.voice.channel.id, 'category_id': ctx.author.voice.category.id})
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
        if (await db.private_channels.find_one({'id': ctx.author.voice.channel.id})):
            await db.private_channels.delete_one({"id": ctx.author.voice.channel.id})
            await ctx.message.add_reaction(check_mark)
        else:
            await message.edit(content='Этот канал не является приватным')

        await asyncio.sleep(3)
        await ctx.message.delete()
        await message.delete()


async def setup(bot):
    await bot.add_cog(privateChannels(bot))
