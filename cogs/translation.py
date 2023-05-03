import discord
from discord import app_commands
from discord.ext import commands
import translators as ts

#async def setup(bot):
    @bot.tree.context_menu()
    async def translate(inter: discord.Interaction, message: discord.Message):
        await inter.response.send_message(ts.google(message.content, to_language=str(inter.locale)), ephemeral=True)
