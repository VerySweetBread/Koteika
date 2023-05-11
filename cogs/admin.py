import discord
from discord import app_commands
from discord.ext import commands

from loguru import logger


@app_commands.guild_only()
class Admin(app_commands.Group):
    @app_commands.command()
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, itr: discord.Interaction, user: discord.Member, reason:str = None, delete_message_mins:int = 0):
        try:
            await user.ban(reason=reason, delete_message_seconds=delete_message_mins*60)
            await itr.response.send_message(f"Member {user.name} was banned")
        except discord.errors.Forbidden:
            await itr.response.send_message("Error: Forbidden", ephemeral=True)


    @app_commands.command()
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, itr: discord.Interaction, user: discord.Member, reason:str = None):
        try:
            await user.kick(reason=reason)
            await itr.response.send_message(f"Member {user.name} was kicked")
        except discord.errors.Forbidden:
            await itr.response.send_message("Error: Forbidden", ephemeral=True)



async def setup(bot: commands.Bot):
    bot.tree.add_command(Admin())

    logger.info(f"{__file__} loaded")
