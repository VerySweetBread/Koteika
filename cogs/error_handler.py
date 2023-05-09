import discord
from discord import app_commands
from discord.ext.commands import Cog
from random import choice
from loguru import logger
from sys import exc_info
from traceback import print_tb, print_exc

class ErrHandler(Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.error(self.on_error)

    async def on_error(self, inter, error):
        logger.error(print_exc())

        errors_text = await self.bot.tree.translator.translate(
            app_commands.locale_str("errors_text"),
            inter.locale,
            app_commands.TranslationContext(
                app_commands.TranslationContextLocation.other,
                "errors_text"
            )
        )
        if errors_text is None:
            errors_text = "The cats dropped the vase again and something broke; "\
            "Today is not the day, it won't work; "\
            "I'm too lazy to do this; "\
            "Something broke. It's not me!"

        await inter.response.send_message(choice(errors_text.split('; ')))

async def setup(bot):
    await bot.add_cog(ErrHandler(bot))
