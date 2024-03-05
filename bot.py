# -*- coding: utf-8 -*-

import json
import traceback
import pretty_errors

from json import load, dump
from os import listdir, getenv
from os.path import isfile, join, getsize, splitext

import discord
from discord.utils import get
from discord.ext import commands, tasks
from discord import app_commands

from random import randint, shuffle, choice, seed
from time import time
from inspect import _empty
from loguru import logger
from discord.ext.commands import HybridCommand

import re
import os
import ast
import nekos
import typing
import asyncio
import sqlite3
import requests
import subprocess
import Levenshtein
import DiscordUtils
from utils.emojis    import *
from utils.checks    import *
from cogs.music     import *
TOKEN = getenv('NATSUKO_TOKEN')
my_id = 710089471835504672


db = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = db.cursor()

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def translate(text, region):
    return text

bot = commands.Bot('!', help_command=None, intents=discord.Intents.all())


bot.owner_id = 459823895256498186


@bot.event
async def on_ready():
    bot.voice_counter = {}

    for dir in os.walk("./cogs"):
        for cog in dir[2]:
            if cog.endswith('.py'):
                logger.info(f"Loading {join(dir[0], cog)}...")
                try:
                    await bot.load_extension(splitext(join(dir[0], cog))[0].replace('/', '.')[2:])
                except discord.ext.commands.errors.ExtensionFailed:
                    logger.error("Failed")
    # await bot.tree.sync()

    # await db.members.update_one({"id": 459823895256498186}, {"$set": {"access_level": "secret"}})

    # if os.path.isfile('reboot'):
    #     with open('reboot', 'r') as f:
    #         try:
    #             data = f.readline()
    #             data = data.split()
    #             mes = await bot.get_channel(int(data[0])).fetch_message(int(data[1]))
    #             await mes.clear_reaction(loading)
    #             await mes.add_reaction(check_mark)
    #
    #             await asyncio.sleep(3)
    #             await mes.delete()
    #         except: pass
    #
    #         await bot.get_channel(773270764522045460) \
    #             .send(embed=discord.Embed(title="Бот перезагружен",
    #                                       color=discord.Color.red()))
    #     os.remove('reboot')
    # else:
    #     await bot.get_channel(773270764522045460) \
    #         .send(embed=discord.Embed(title="Бот запущен",
    #                                   color=discord.Color.red()))

    logger.info('Я живой, блин!')

CSF = discord.Object(id=822157545622863902)


@bot.command()
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx, count: int):
    count += 1

    while count > 100:
        await ctx.channel.purge(limit=100)
        count -= 100
    await ctx.channel.purge(limit=count)



@bot.command(name='eval')
@commands.is_owner()
async def eval_fn(ctx, timeout: typing.Optional[int] = 10, *, cmd):
    fn_name = "_eval_expr"

    cmd = cmd.strip("` ")

    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__,
        'get': get
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    try:
        await eval(f"{fn_name}()", env)
    except Exception as e:
        await ctx.message.reply(repr(e))


@bot.command(aliases=["reload"], brief="Перезагружает бота")
@commands.is_owner()
async def reboot(ctx):
    if os.name == 'posix':
        await ctx.message.add_reaction(loading)
        with open('reboot', 'w') as f:
            f.write(f"{ctx.message.channel.id} {ctx.message.id}")
        os.system('pm2 restart Koteika')


# @bot.command(brief="Управление консолью")
# @commands.check(is_secret)
# async def cmd(ctx, *, command):
#     try:
#         proc = await asyncio.create_subprocess_shell(command,
#                                                      shell=True,
#                                                      stdout=subprocess.PIPE,
#                                                      stderr=subprocess.PIPE,
#                                                      stdin=subprocess.PIPE)
#         proc_data = await proc.communicate()
#         e = discord.Embed(title="Скрипт завершился без ошибок" if proc_data[1] == b'' else "Ошибка",
#                           color=discord.Color.green() if proc_data[1] == b'' else discord.Color.red())
#         e.add_field(name="STDOUT", value=f"```{proc_data[0][-994:].decode('utf-8')}```") \
#             if proc_data[0] != b'' else None
#         e.add_field(name="STDERR", value=f"```{proc_data[1][-994:].decode('utf-8')}```") \
#             if proc_data[1] != b'' else None
#
#         await ctx.message.reply(embed=e)
#     except Exception as e:
#         logger.error(repr(e))


# # TODO: to application commands 
# @bot.command(aliases=["vmute", "v_mute", "v_m", "vm"], brief="Выключает микрфоны всех участников ГК")
# @commands.has_guild_permissions(administrator=True)
# async def voice_mute(ctx):
#     channel = ctx.message.author.voice.channel
#
#     if channel is not None:
#         for i in channel.members:
#             await i.edit(mute=True)
#         await ctx.message.add_reaction(check_mark)
#
#     else:
#         await channel.send("Ты не находишься в ГК")
#         await ctx.message.add_reaction(XX)
#
#     await asyncio.sleep(3)
#     await ctx.message.delete()
#
#
# @bot.command(aliases=["vunmute", "v_unmute", "v_unm", "vu"], brief="Влючает микрфоны всех участников ГК")
# @commands.has_guild_permissions(administrator=True)
# async def voice_unmute(ctx):
#     channel = ctx.message.author.voice.channel
#
#     if channel is not None:
#         for i in channel.members:
#             await i.edit(mute=False)
#         await ctx.message.add_reaction(check_mark)
#
#     else:
#         await channel.send("Ты не находишься в ГК")
#         await ctx.message.add_reaction(XX)
#
#     await asyncio.sleep(3)
#     await ctx.message.delete()


# @bot.command(brief="Выводит права участника сервера (по умолчанию - кота)")
# async def perms(ctx, user: typing.Union[discord.Member, int] = None):
#     if user is None:
#         user = ctx.author.id
#     elif type(user) == discord.Member:
#         user = user.id
#
#     p = {}
#     out = ''
#     for i in ['create_instant_invite', 'kick_members', 'ban_members', 'administrator', 'manage_channels',
#               'manage_guild', 'add_reactions', 'view_audit_log', 'priority_speaker', 'stream', 'read_messages',
#               'send_messages', 'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files',
#               'read_message_history', 'mention_everyone', 'external_emojis', 'view_guild_insights', 'connect', 'speak',
#               'mute_members', 'deafen_members', 'move_members', 'use_voice_activation', 'change_nickname',
#               'manage_nicknames', 'manage_roles', 'manage_webhooks', 'manage_emojis']:
#         p[i] = False
#
#     perms = ctx.guild.get_member(user).guild_permissions
#     for i in iter(perms):
#         p[i[0]] = i[1]
#
#     for i in p.keys():
#         if p[i]:
#             out += '+ '
#         else:
#             out += '- '
#         out += i + '\n'
#
#     await ctx.send('```diff\n' + out + '```')


async def check(itr: discord.Interaction):
    if not itr.channel.permissions_for(itr.guild.me).send_messages:
        await itr.response.send_message("Commands are not allowed here", ephemeral=True)
        return False
    return True

bot.tree.interaction_check = check

bot.run(TOKEN)

