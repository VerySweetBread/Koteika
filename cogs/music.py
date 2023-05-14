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
    info:       dict[str, any]

@dataclass
class Channel:
    adder: discord.Member
    cur_pos: int
    queue: list[Song]
    context: discord.Interaction
    # skip_policy: Enum "everyone"


class Music(commands.Cog, name="Музыка"):
    def __init__(self, bot):
        self.bot = bot
        self.queue: dict[int, Channel] = {}

    
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
        
        await inter.response.defer(thinking=True)

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

        self.queue[channel.id].queue.append(Song(url, inter.user, info))

        await inter.edit_original_response(content="Добавлена новая песня в очередь")

        if not (client.is_playing() or client.is_paused()):
            self.__play(inter, info)
    

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
    

    def __play(self, inter, info):
        try:
            URL = info['url']
        except:
            URL = url
            logger.debug(URL)

        audio_source = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        inter.guild.voice_client.play(audio_source, after=lambda error: self.__next(inter, error))

        logger.debug(inter)
        asyncio.run_coroutine_threadsafe(self.__send_embed(inter, info), self.bot.loop)


    async def __send_embed(self, inter, info):
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
        await inter.channel.send(embed=embed)


    async def __end_of_queue(self, inter):
        await inter.channel.send("В очереди больше не осталось песен")


    def __next(self, inter, error=None):
        if error:
            logger.error(error)
            return

        inter.guild.voice_client.stop()

        queue = self.queue[inter.user.voice.channel.id]
        queue.cur_pos += 1
        logger.debug((len(queue.queue), queue.cur_pos))
        if len(queue.queue) == queue.cur_pos:
            asyncio.run_coroutine_threadsafe(self.__end_of_queue(inter), self.bot.loop)
            return

        #logger.debug([query["music_pos"]])
        info = queue.queue[queue.cur_pos].info
        self.__play(inter, info)


async def setup(bot):
    await bot.add_cog(Music(bot))
