import discord
import yt_dlp as youtube_dl
import functools
import asyncio

from loguru import logger
from json import dumps
from discord.ext import commands

from bot import db

class Music(commands.Cog, name="Музыка"):
    def __init__(self, bot):
        self.bot = bot
        self.query = {}

    def play_(self, ctx, url):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        try:
            URL = info['url']
        except:
            URL = url
            logger.debug(URL)
        with open("/home/pi/temp", 'w') as f:
            f.write(dumps(info))
        audio_source = discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)
        ctx.guild.voice_client.play(audio_source, after=lambda error: self.next_(ctx, error))

        try:    
            asyncio.create_task(self.send_embed_(ctx, info, url))
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_debug(True)
            loop.run_until_complete(self.send_embed_(ctx, info, url))
            loop.stop()

    async def send_embed_(self, ctx, info, url):
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
        await ctx.send(embed=embed)

    async def end_of_query_(self, ctx):
        await ctx.send("В очереди больше не осталось песен")


    @commands.command()
    async def play(self, ctx, url, query: bool = True):        
        channel = ctx.author.voice.channel

        if ctx.author.voice is None:
            await ctx.send("Ты не в ГК")
            return
        if ctx.guild.voice_client is None:
            await channel.connect()
        elif ctx.author.voice.channel != ctx.guild.voice_client.channel:
            await ctx.send(f"Занято каналом {ctx.guild.voice_client.channel.mention}")
            return

        client = ctx.guild.voice_client

        if url=="":
            url = self.query[str(channel.id)][0]
            del self.query[str(channel.id)][0]


        if query:
            if client.is_playing() or client.is_paused():
                if str(channel.id) not in self.query.keys():
                    self.query[str(channel.id)] = {
                        "requester_id": "ctx.author.id",
                        "music_pos": -1,
                        "query": [],
                        "context": ctx
                    }
                self.query[str(channel.id)]["query"].append(url)
                await ctx.send("Добавлена новая песня в очередь")
                return

        self.play_(ctx, url)
        
    @commands.command()
    async def stop(self, ctx):
        ctx.guild.voice_client.stop()

    @commands.command()
    async def pause(self, ctx):
        ctx.guild.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        ctx.guild.voice_client.resume()

    @commands.command()
    async def disconnect(self, ctx):
        await ctx.guild.voice_client.disconnect()

    @commands.command()
    async def next(self, ctx):
        self.next_(ctx)

    def next_(self, ctx, error=None):
        ctx.guild.voice_client.stop()
        query = self.query[str(ctx.author.voice.channel.id)]
        query["music_pos"] = query["music_pos"] + 1
        if len(query["query"]) < query["music_pos"]:
            try:
                asyncio.create_task(self.end_of_query_(ctx))
            except:
                pass
            return

        url = query["query"][query["music_pos"]]
        self.play_(ctx, url)


async def setup(bot):
    await bot.add_cog(Music(bot))
