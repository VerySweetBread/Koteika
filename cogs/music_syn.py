import discord
import shlex
from subprocess import Popen, PIPE

from discord import app_commands
from discord.ext import commands

from mido import Message, MidiFile, MidiTrack, second2tick

class MusicSyn(commands.Cog):
    @app_commands.command(description="Music MIDI synthesis")
    @app_commands.describe(notes="MIDI notes (comma separated)")
    async def make_music(self, inter, notes: str):
        notes = notes.split(', ')

        if list(filter(lambda x: not x.isdigit(), notes)):
            await inter.response.send_message("Ноты должны быть числами от 0 до 127")
            return

        notes = list(map(int, notes))
        
        if list(filter(lambda x: x < 0 or 127 < x, notes)):
            await inter.response.send_message("Ноты должны быть от 0 до 127")
            return

        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        time = int(second2tick(0.1, 480, 500000))

        for note in notes:
            track.append(Message('note_on', note=note, time=time))
            track.append(Message('note_off', note=note, time=time))

        mid.save(f'tmp/{inter.id}.mid')

        with Popen(shlex.split(f'timidity tmp/{inter.id}.mid -Ow -o -'), stdout=PIPE) as timidity:
            with Popen(shlex.split(f'ffmpeg -i - -acodec libmp3lame -ab 64k tmp/{inter.id}.mp3'), stdout=PIPE, stdin=PIPE) as ffmpeg:
                ffmpeg.stdin.write(timidity.stdout.read())

        with open(f'tmp/{inter.id}.mp3', 'rb') as f:
            await inter.response.send_message(file=discord.File(f))

async def setup(bot):
    await bot.add_cog(MusicSyn())
