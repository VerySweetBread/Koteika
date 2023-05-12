import discord
import yt_dlp as youtube_dl
import functools
import asyncio

from loguru import logger
from json import dumps
from discord import app_commands
from discord.ext import commands
from dataclasses import dataclass

from bot import db

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

# TODO: locale

@dataclass
class Song:
    register:   int
    url:        str
    info:       Dict[str, Any]

@dataclass
class Channel:
    adder: discord.Member
    cur_pos: int
    queue: List[Song]
    context: discord.Interaction
    # skip_policy: Enum "everyone"


class Music(commands.Cog, name="Музыка"):
    def __init__(self, bot):
        self.bot = bot
        self.queue: Dict[int, Channel] = {}

    def play_(self, inter, info):
        try:
            URL = info['url']
        except:
            URL = url
            logger.debug(URL)

        audio_source = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        inter.guild.voice_client.play(audio_source, after=lambda error: self.next_(inter, error))

        asyncio.run_coroutine_threadsafe(self.send_embed_(inter, info), self.bot.loop)

    async def send_embed_(self, inter, info):
        embed = discord.Embed (
            title=info["title"],
            url=info['url'],
            description=info["description"]
        )
        embed.set_author (
            name=info["uploader"],
            url=info["uploader_url"]
        )
        embed.set_thumbnail( url=info["thumbnail"] )
        try:
            await inter.response.send_message(embed=embed)
        except:
            await inter.channel.send(embed=embed)

    async def end_of_queue_(self, inter):
        await inter.channel.send("В очереди больше не осталось песен")

    @app_commands.command(description="Plays music from popular platforms")
    @app_commands.describe(url="URL from Youtube/RuTube and other platforms")
    async def play(self, inter, url: str):
        logger.debug(asyncio.get_running_loop())
        channel = inter.user.voice.channel

        if inter.user.voice is None:
            await inter.response.send_message("Ты не в ГК")
            return
        if inter.guild.voice_client is None:
            await channel.connect()
            self.queue[channel.id] = Channel(inter.user, 0, [], inter)
        elif inter.user.voice.channel != inter.guild.voice_client.channel:
            await inter.response.send_message(f"Занято каналом {inter.guild.voice_client.channel.mention}")
            return

        client = inter.guild.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

        self.queue[channel.id].queue.append(Song(url, inter.user, info))

        if client.is_playing() or client.is_paused():
            await inter.response.send_message("Добавлена новая песня в очередь")
            return
        else:
            inter.guild.voice_client.stop()

        self.play_(inter, info)
        
    @app_commands.command()
    async def stop(self, inter):
        queue = self.queue[inter.user.voice.channel.id]
        queue.cur_pos = len(queue.queue)-1
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
        inter.guild.voice_client.stop()

    @app_commands.command(name='queue')
    async def _queue(self, inter):
        queue = self.queue[inter.user.voice.channel.id]
        text = ''
        for pos, item in enumerate(queue['queue']):
            if queue.cur_pos == pos: text += '>>> '
            else: text += '    '

            text += f"{pos+1}. "
            text += item.info['title']
            text += '\n    - Запросил: ' + item.requester.name

            text += '\n'
        await inter.response.send_message(f"```\n{text}\n```")
        

    def next_(self, inter, error=None):
        if error:
            logger.error(error)
            return

        inter.guild.voice_client.stop()

        queue = self.queue[inter.user.voice.channel.id]
        queue.cur_pos += 1
        logger.debug((len(queue.queue), queue.cur_pos))
        if len(queue.queue) == queue.cur_pos:
            asyncio.run_coroutine_threadsafe(self.end_of_queue_(inter), self.bot.loop)
            return

        #logger.debug([query["music_pos"]])
        info = queue.queue[queue.cur_pos].info
        self.play_(inter, info)


async def setup(bot):
    await bot.add_cog(Music(bot))
