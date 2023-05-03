from asyncio import sleep
from os import system
from subprocess import Popen, PIPE, TimeoutExpired

from discord.ext import commands
from cogs.emojis import *
from cogs.checks import is_secret


class Bomber(commands.Cog):
    @commands.command(brief="Спаммер",
                      help="""Номер телефона в международном формате без + в начале
                            Режим флуда (1 - СМС, 2 - звонки, 3 - оба)
                            Сколько времени спамить (в секундах). Не больше 2х минут (120с)""")
    @commands.check(is_secret)
    async def bomber(self, ctx, num: int, type: int = 1, time: int = 30):
        await ctx.message.add_reaction(loading)
        with Popen(["/home/pi/Cat/bomber.sh", str(num), str(type), str(time)], stdin=PIPE) as proc:
            proc.stdin.write(b'\n')

            try:
                if proc.wait(time+5) == 0:
                    await ctx.message.add_reaction(check_mark)
                else:
                    await ctx.message.add_reaction(XX)
            except TimeoutExpired:
                await ctx.message.add_reaction(XX)

        await sleep(3)
        await ctx.message.delete()


# def setup(bot):
#     bot.add_cog(Bomber(bot))
