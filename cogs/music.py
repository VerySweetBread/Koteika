import discord
import yt_dlp as youtube_dl
import functools
import asyncio

from loguru import logger
from json import dumps
from discord import app_commands
from discord.app_commands import Choice

import enum
from dataclasses import dataclass

from bot import db

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

# TODO: locale

@dataclass
class Song:
    url:        str
    requester:  discord.Member
    info:       dict[str, any]

class RepeatStatus(enum.Enum):
    once            = 0
    one_song        = 1
    whole_playlist  = 2

@dataclass
class Channel:
    adder: discord.Member
    cur_pos: int
    queue: list[Song]
    context: discord.Interaction
    # skip_policy: Enum "everyone"
    repeat_status: int = RepeatStatus.once.value


@app_commands.guild_only()
class Music(app_commands.Group, name="music"):
    def __init__(self, bot):
        super().__init__()
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
        await inter.response.send_message("Переключено")

    @app_commands.command()
    @app_commands.choices(status=[
        Choice(name="once", value=RepeatStatus.once.value),
        Choice(name="one song", value=RepeatStatus.one_song.value),
        Choice(name="whole playlist", value=RepeatStatus.whole_playlist.value)
    ])
    async def repeat(self, inter, status: Choice[int]):
        channel_info = self.queue[inter.user.voice.channel.id]
        channel_info.repeat_status = status.value
        await inter.response.send_message("Set repeat: `{}`".format(status.name))


    @app_commands.command(name='queue')
    async def _queue(self, inter):
        queue = self.queue[inter.user.voice.channel.id]
        text = ''
        for pos, item in enumerate(queue.queue):
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
        if queue.repeat_status != RepeatStatus.one_song.value:
            queue.cur_pos += 1

        logger.debug((len(queue.queue), queue.cur_pos))
        if len(queue.queue) == queue.cur_pos:
            if queue.repeat_status == RepeatStatus.whole_playlist.value:
                queue.cur_pos = 0
            else:
                asyncio.run_coroutine_threadsafe(self.__end_of_queue(inter), self.bot.loop)
                return

        #logger.debug([query["music_pos"]])
        info = queue.queue[queue.cur_pos].info
        self.__play(inter, info)


async def setup(bot):
    bot.tree.add_command(Music(bot))
