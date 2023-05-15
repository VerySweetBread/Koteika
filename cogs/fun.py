import discord
import requests

import utils.XOR as XOR
import utils.FFC as FFC

from discord import app_commands
from discord.ext import commands
from os import remove
from os.path import splitext, join

tmp_dir = "tmp"

class Fun(commands.Cog):
    htip_gr = app_commands.Group(name="htip", description="Hide text in picture")

    @htip_gr.command()
    async def write(self, itr: discord.Interaction, text: str, pic: discord.Attachment, key: str = None):
        if key is not None:
            text = XOR.char_encode(text, key)

        filename = f"{itr.id}.pic.filename"
        fln, ext = splitext(filename)
        if ext not in ('.jpg', '.png'):
            await itr.response.send_message("Supported only JPEG and PNG")
            return

        url = pic.url
        img = requests.get(url)
        with open(join(tmp_dir, filename), 'wb') as img_file:
            img_file.write(img.content)

        FFC.write(join(tmp_dir, filename), join(tmp_dir, f'{fln}.secret{ext}'), text)
        with open(join(tmp_dir, f'{fln}.secret{ext}'), 'rb') as f:
            await itr.response.send_message(file=discord.File(f))
        remove(join(tmp_dir, filename))
        remove(join(tmp_dir, f'{fln}.secret{ext}'))


    @htip_gr.command()
    async def read(self, itr: discord.Interaction, pic: discord.Attachment, key: str = None):
        filename = f"{itr.id}.pic.filename"

        fln, ext = splitext(filename)
        if ext not in ('.jpg', '.png'):
            await itr.response.send_message('Supported only JPEG or PNG')
            return

        url = pic.url
        img = requests.get(url)
        with open(join(tmp_dir, filename), 'wb') as img_file:
            img_file.write(img.content)

        secret_text = FFC.read(join(tmp_dir, filename))
        if key is not None:
            secret_text = XOR.char_encode(secret_text, key)
        await itr.response.send_message(secret_text)

        remove(join(tmp_dir, filename))

async def setup(bot): 
    await bot.add_cog(Fun())
