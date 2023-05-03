import discord

from discord                import app_commands
from discord.app_commands   import Choice
from discord.ext            import commands, tasks
from os                     import listdir
from os.path                import splitext

class Stickers(commands.Cog, name="Стикеры"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sl"])
    async def sticker_list(self, ctx):
        if ctx.guild is not None:
            color = ctx.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        
        list_ = listdir("/home/pi/Koteika/Stickers")
        embed = discord.Embed(title="Стикеры", description="\n".join([f"{i+1}: {list_[i]}" for i in range(len(list_))]), color=color)
        await ctx.send(embed=embed)

    @commands.command(name="send_sticker", aliases=["ss"])
    async def _send_sticker(self, ctx, sticker: int, *, content=""):
        if ctx.guild is not None:
            color = ctx.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        embed = discord.Embed(color=color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        with open(f"/home/pi/Koteika/Stickers/{listdir('/home/pi/Koteika/Stickers')[sticker-1]}", 'rb') as f:
            await ctx.send(content, file=discord.File(f), embed=embed, reference=ctx.message.reference)
            try: await ctx.message.delete()
            except: pass

    @app_commands.command(name="sticker", description="Отправляет стикер")
    @app_commands.guilds(discord.Object(822157545622863902))
    @app_commands.describe(sticker="Стикер")
    @app_commands.choices(sticker=[Choice(name=splitext(i)[0], value=i) for i in listdir("/home/pi/Koteika/Stickers")])
    async def send_sticker(self, inter, sticker: Choice[str]):
        with open(f"/home/pi/Koteika/Stickers/{sticker.value}", 'rb') as f:
            await inter.response.send_message(file=discord.File(f))
    

async def setup(bot):
    await bot.add_cog(Stickers(bot))
