import discord
import typing
from discord.ext import commands

from cogs._colors import choise_light_color
from cogs.emojis import *


# async def emoji_controll(func):
#     await func.ctx.add_reaction(loading)
#
#     try:
#         func()
#         await func.ctx.add_reaction(check_mark)
#     except:
#         await func.ctx.add_reaction(XX)
#
#     try:
#         await func.ctx.clear_reaction(loading)
#     except:
#         await func.ctx.remove_reaction(loading)


class Moderation(commands.Cog, name="Модерация"):
    """Модерация"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="сообщения",
                    brief="Работа с сообщениями")
    async def messages(self, ctx):
        # embed = discord.Embed(title="Список доступных методов:",
        #                       color=choise_light_color)
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Список комманд можно посмотреть в `{ctx.prefix}help сообщения`")

    @messages.command(brief="Публикация сообщения",
                      help="Публикация сообщения в новостном чате",
                      name="опубликовать")
    # @emoji_controll()
    async def publish(self, ctx, message_id: int, channel_id: int): # , guild_id: typing.Optional[int] = None):
        # if guild_id is not None: guild_id = ctx.guild.id

        # await ctx.message.add_reaction(loading)

        # guild = self.bot.get_guild(guild_id)
        # if guild is not None:
        channel = ctx.guild.get_channel(channel_id)
        if channel is not None:
            mes = await channel.fetch_message(message_id)
            if mes is not None:
                await mes.publish()
                await ctx.add_reaction(check_mark)
            else:
                await ctx.send("Неккоректный id сообщения")
        else:
            await ctx.send("Неккоректный id канала")
        # else:
        #     await ctx.send("Неккоректный id сервера")

        # await ctx.message.add_reaction()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
