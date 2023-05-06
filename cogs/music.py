import discord
import yt_dlp as youtube_dl
import functools
import asyncio

from loguru import logger
from json import dumps
from discord import app_commands
from discord.ext import commands

from bot import db

# TODO: locale

class Music(commands.Cog, name="Музыка"):
    def __init__(self, bot):
        self.bot = bot
        self.query = {}

    def play_(self, inter, url):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        try:
            URL = info['url']
        except:
            URL = url
            logger.debug(URL)
        with open("tmp/tmp.log", 'w') as f:
            f.write(dumps(info))
        audio_source = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        inter.guild.voice_client.play(audio_source, after=lambda error: self.next_(inter, error))

        try:    
            asyncio.create_task(self.send_embed_(inter, info, url))
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_debug(True)
            loop.run_until_complete(self.send_embed_(inter, info, url))
            loop.stop()

    async def send_embed_(self, inter, info, url):
        embed = discord.Embed (
            title=info["title"],
            url=url,
            description=info["description"]
        )
        embed.set_author (
            name=info["uploader"],
            url=info["uploader_url"]
        )
        embed.set_thumbnail( url=info["thumbnail"] )
        await inter.response.send_message(embed=embed)

    async def end_of_query_(self, inter):
        await inter.response.send_message("В очереди больше не осталось песен")


    @app_commands.command(description="Plays music from popular platforms")
    @app_commands.describe(
        url="URL from Youtube/RuTube and other platforms",
        query="Add music to query"
    )
    async def play(self, inter, url: str):        
        channel = inter.user.voice.channel

        if inter.user.voice is None:
            await inter.response.send_message("Ты не в ГК")
            return
        if inter.guild.voice_client is None:
            await channel.connect()
        elif inter.user.voice.channel != inter.guild.voice_client.channel:
            await inter.response.send_message(f"Занято каналом {inter.guild.voice_client.channel.mention}")
            return

        client = inter.guild.voice_client

        if url=="":
            url = self.query[str(channel.id)][0]
            del self.query[str(channel.id)][0]

        if str(channel.id) not in self.query.keys():
            self.query[str(channel.id)] = {
                "requester_id": inter.user.id,
                "music_pos": -1,
                "query": [],
                "context": inter
            }

        if client.is_playing() or client.is_paused():
            if query:
                self.query[str(channel.id)]["query"].append(url)
                logger.debug("\n".join(self.query[str(channel.id)]['query']))
                await inter.response.send_message("Добавлена новая песня в очередь")
                return
            else:
                inter.guild.voice_client.stop()

        self.play_(inter, url)
        
    @app_commands.command()
    async def stop(self, inter):
        inter.guild.voice_client.stop()
        await inter.response.send_message("Остановлено")

    @app_commands.command()
    async def pause(self, inter):
        inter.guild.voice_client.pause()
        await inter.response.send_message("Поставлено на паузу")

    @app_commands.command()
    async def resume(self, inter):
        inter.guild.voice_client.resume()
        await inter.response.send_message("Снято с паузы")

    @app_commands.command()
    async def disconnect(self, inter):
        await inter.guild.voice_client.disconnect()
        await inter.response.send_message("Отключено")

    @app_commands.command()
    async def next(self, inter):
        self.next_(inter)

    def next_(self, inter, error=None):
        inter.guild.voice_client.stop()
        query = self.query[str(inter.user.voice.channel.id)]
        query["music_pos"] = query["music_pos"] + 1
        logger.debug((len(query["query"]), query["music_pos"]))
        if len(query["query"]) < query["music_pos"]:
            try:
                asyncio.run(self.end_of_query_(inter))
                # asyncio.create_task(self.end_of_query_(inter))
            except:
                pass
            return

        url = query["query"][query["music_pos"]]
        self.play_(inter, url)


async def setup(bot):
    await bot.add_cog(Music(bot))
