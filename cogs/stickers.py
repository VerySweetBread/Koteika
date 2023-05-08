import discord

from discord                import app_commands
from discord.app_commands   import Choice
from discord.ext            import commands, tasks
from os                     import listdir
from os.path                import splitext, join

dir = "Stickers"

class Stickers(commands.Cog, name="Стикеры"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sl"])
    @app_commands.guilds(discord.Object(822157545622863902))
    async def sticker_list(self, ctx):
        if ctx.guild is not None:
            color = ctx.guild.me.color
            if color == discord.Color.default():
                color = discord.Color(0xaaffaa)
        else:
            color = discord.Color(0xaaffaa)

        
        list_ = listdir(dir)
        embed = discord.Embed(title="Стикеры", description="\n".join([f"{i+1}: {list_[i]}" for i in range(len(list_))]), color=color)
        await ctx.send(embed=embed)

    @app_commands.command(name="sticker", description="Отправляет стикер")
    @app_commands.guilds(discord.Object(822157545622863902))
    @app_commands.describe(sticker="Стикер")
    @app_commands.choices(sticker=[Choice(name=splitext(i)[0], value=i) for i in listdir(dir)])
    async def send_sticker(self, inter, sticker: Choice[str]):
        with open(join(dir, sticker.value), 'rb') as f:
            await inter.response.send_message(file=discord.File(f))
    

async def setup(bot):
    await bot.add_cog(Stickers(bot))
