import discord
from discord import app_commands
from discord.ext import commands
from simpledemotivators import Demotivator as Dem
from os import remove
from os.path import join
from loguru import logger

class Demotivator(commands.Cog):
    @app_commands.command()
    async def demotivator(self, inter: discord.Interaction, title: str, text: str, image: discord.Attachment):
        logger.debug((title, text))

        if not "image" in image.content_type:
            await inter.response.send_message("Это не изображение")
            return

        logger.debug("Meow")
        filename = join("/home/pi/Koteika/tmp", f"{inter.id}_{image.filename}")
        logger.debug(filename)
        await image.save(filename)
        Dem(title, text).create(filename, font_name="FreeSans.ttf")
        with open(filename) as f:
            await inter.response.send_message(file=discord.File(f))
        remove(filename)

async def setup(bot):
    await bot.add_cog(Demotivator())
