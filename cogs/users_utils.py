import discord
from discord.ext.commands import Bot

async def setup(bot: Bot):
    @bot.tree.context_menu()
    async def show_avatar(inter: discord.Interaction, user: discord.Member):
        e = discord.Embed(title="Аватар пользователя")
        e.set_image(url=user.display_avatar.url)
        await inter.response.send_message(embed=e)
