import discord
from discord.ext import commands
from discord import app_commands
from os.path import splitext
from os.path import join as joinpath
from os import mkdir, rmdir, remove

from cairosvg import svg2png


class FileExt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            files = []
            mkdir(joinpath("/home/pi/Koteika/tmp", str(message.id)))
            if list(filter(lambda x: splitext(x.filename)[1] in ('.mkv', '.svg'), message.attachments)):
                m = await message.reply("Конвертация...")


            # MKV
            for at in filter(lambda x: x.filename.endswith('.mkv'), message.attachments):
                await at.save(fp=joinpath("/home/pi/Koteika/tmp", str(message.id), at.filename))
                import ffmpeg 
                (
                    ffmpeg
                    .input(joinpath("/home/pi/Koteika/tmp", str(message.id), at.filename))
                    .output(joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.mp4'))
                    .run()
                )
                remove(joinpath("/home/pi/Koteika/tmp", str(message.id), at.filename))
                with open(joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.mp4'), 'rb') as f:
                    files.append( discord.File(f, spoiler=at.is_spoiler(), filename=splitext(at.filename)[0]+'.mp4') )
                remove(joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.mp4'))

            # SVG
            for at in filter(lambda x: x.filename.endswith('.svg'), message.attachments):
                code = await at.read()
                code = code.decode("utf-8")
                svg2png(bytestring=code, write_to=joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.png'))
                
                with open(joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.png'), 'rb') as f:
                    files.append( discord.File(f, spoiler=at.is_spoiler(), filename=splitext(at.filename)[0]+'.png') )
                remove(joinpath("/home/pi/Koteika/tmp", str(message.id), splitext(at.filename)[0]+'.png'))


            if files:
                await message.reply(files=files)
                await m.delete()

            rmdir(joinpath("/home/pi/Koteika/tmp", str(message.id)))

async def setup(bot):
    await bot.add_cog(FileExt(bot))
