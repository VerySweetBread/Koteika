# -*- coding: utf-8 -*-

import json
import traceback
from json import load, dump
from os import listdir, getenv
from os.path import isfile, join, getsize

import XOR

import discord
from discord.utils import get
from discord.ext import commands, tasks
from discord import app_commands

from random import randint, shuffle, choice, seed
from time import time
from inspect import _empty
from pymongo import MongoClient
from loguru import logger
from discord.ext.commands import HybridCommand

import re
import os
import ast
import FFC
import nekos
import typing
import asyncio
import requests
import subprocess
import Levenshtein
import DiscordUtils
from cogs.emojis    import *
from cogs.checks    import *
from cogs.translate import *
from cogs.music     import *
TOKEN = getenv('NATSUKO_TOKEN')
my_id = 710089471835504672

db = MongoClient('localhost', 27017).Koteika

if os.path.exists('prefixes.json'):
    with open('prefixes.json', 'r') as f:
        prefs = load(f)

if not os.path.exists('tmp'):
    os.mkdir('tmp')

else:
    prefs = {"default": "*"}


def NFIF(path):
    return len([f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))])


# def func_check(v):                                            # TODO: Выявить ошибку и использовать
#     def premeow(*args, **kwargs):
#         async def meow(ctx):
#             try:
#                 await ctx.message.add_reaction(loading)
#                 await func(*args, **kwargs)
#                 await ctx.message.add_reaction(check_mark)
#             except Exception as e:
#                 print(repr(e))
#                 await ctx.message.add_reaction(XX)
#
#             await asyncio.sleep(3)
#             await ctx.message.delete()
#         return meow
#     return premeow


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def region_to_str(_): return "RU"       # TODO: Заменить на нормальный код -_-

def add_user_to_DB(member):
    # if member is not discord.Member: return
    ids = [i["id"] for i in db.members.find()]
    if member.id not in ids:
        db.members.insert_one({"id": member.id,
                               "name": member.name,
                               "access_level": "gray",
                               "language": region_to_str("Meow"),   # TODO: Ну, очевидно
                               "money": 0,
                               "exp": 0,
                               "level": 0,
                               "history": {
                                   "hour": {},
                                   "day": {},
                               },
                               "max_level": 0,
                               "last_mess_time": 0,
                               "stocks": {},
                               "guild_stat": {}
                               })

def translate(text, region):
    return text

async def prefixes(bot, message):
    pattern = re.compile(r'/(?:^|[^а-яёa-z]|[,.])(?:(?:ко(?:т(?:(?:е(?:йк|ньк))|(?:ик)|(?:ан)|(?:[её]нок)|(?:я['
                         r'рт]))?|(?:шак)))(?:[иаыуэя]|(?:ов)|(ом))?)(?:[^а-яёa-z]|$)/gm', flags=re.IGNORECASE)
    match = pattern.search(message.content)

    def check():
        return type(message.channel) == discord.channel.DMChannel or str(message.guild.id) not in prefs.keys()

    return commands.when_mentioned_or(prefs[str(message.guild.id)] if not check() else prefs["default"],
                                      match[0])(bot, message) if match else \
        commands.when_mentioned_or(prefs[str(message.guild.id)] if not check() else prefs["default"])(bot, message)

intents=discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=prefixes, help_command=None, intents=intents)
# bot = commands.Bot(command_prefix=prefixes, intents=discord.Intents.all())


bot.code_lines = 0
bot.code_size = 0
#code_lines = 0  # num_lines = sum(1 for line in open('bot.py'))
#code_size = 0  # getsize("bot.py")

max_cog_name_len = max([len(cog) for cog in os.listdir('./cogs') if cog.endswith('.py')])

bot.add_check(is_not_black)
# bot.add_check(is_white)

bot.owner_id = 459823895256498186

my_roles = []
privat_channels = []
last_DM = bot.owner_id
last_channel = bot.get_channel(745689950460051546)

notification = {}
players = {}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



@tasks.loop(seconds=5)
async def change_activity():
    #await asyncio.sleep(5)
    #await bot.change_presence(activity=discord.Activity(name='обработку российского ботнета',
    #                                                    type=discord.ActivityType.playing))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.Activity(name=f'на {len(bot.guilds)} сервер(a/ов)',
                                                        type=discord.ActivityType.watching))
    #await asyncio.sleep(5)
    #await bot.change_presence(activity=discord.Activity(name='радость и счастье',
    #                                                    type=discord.ActivityType.streaming))
    #await asyncio.sleep(5)
    #await bot.change_presence(activity=discord.Activity(name='мяукании в пустототе',
    #                                                    type=discord.ActivityType.competing))
    await asyncio.sleep(5)
    await bot.change_presence(activity=discord.Activity(name=f'на {bot.code_lines} строк и {bot.code_size//2**10} Кб '
                                                             'сыворотки костылей, велосипедов и кода',
                                                        type=discord.ActivityType.watching))

    seed(int(time()))


# @tasks.loop(seconds=10)
# async def v_delete():
#     v_channels = get(get(bot.guilds, id=701726806377496587)
#                      .categories, id=733787908129030194) \
#         .voice_channels
#
#     for channel in v_channels:
#        if channel.id != 733788167236223056:
#             if not channel.members:
#                 await channel.delete()


@bot.event
async def on_ready():
    bot.voice_counter = {}

    try:
        await bot.load_extension("cogs.settings.server")
    except Exception as e:
        logger.error(repr(e))

    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            try:
                logger.info(f"Загрузка {cog.capitalize()}...")
                await bot.load_extension(f'cogs.{cog.replace(".py", "")}')

                code_lines_ = num_lines = sum(1 for _ in open("cogs/"+cog))
                code_size_ = getsize("cogs/"+cog)

                bot.code_lines += code_lines_
                bot.code_size += code_size_

                logger.info(f">   {cog.capitalize()} загружен{' '*(max_cog_name_len-len(cog))}\tСтрок: {code_lines_}\tРазмер: {code_size_}")
            except Exception as e:
                logger.debug(repr(e))

    logger.info(f"{bot.code_lines}\t{bot.code_size}")
    db.members.update_one({"id": 459823895256498186}, {"$set": {"access_level": "secret"}})

    if os.path.isfile('reboot'):
        with open('reboot', 'r') as f:
            try:
                data = f.readline()
                data = data.split()
                mes = await bot.get_channel(int(data[0])).fetch_message(int(data[1]))
                await mes.clear_reaction(loading)
                await mes.add_reaction(check_mark)

                await asyncio.sleep(3)
                await mes.delete()
            except: pass

            await bot.get_channel(773270764522045460) \
                .send(embed=discord.Embed(title="Бот перезагружен",
                                          color=discord.Color.red()))
        os.remove('reboot')
    else:
        await bot.get_channel(773270764522045460) \
            .send(embed=discord.Embed(title="Бот запущен",
                                      color=discord.Color.red()))

    logger.info('Я живой, блин!')

    #for guild in bot.guilds:
    #    for member in guild.members:
    #        add_user_to_DB(member)

    #change_activity.start()
#     v_delete.start()


async def on_message_handler(message):
    channel = message.channel
    user = message.author

    global last_channel
    last_channel = channel

    # Обработка команд (пре-подготовка)
    if user.name != 'Котейка':
        add_user_to_DB(user)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    await on_message_handler(message)


@bot.command(pass_content=True)
async def mirror(ctx, time: int, *, atr):
    await ctx.message.delete()
    async with ctx.typing():
        await asyncio.sleep(time)
        await ctx.send(atr)

CSF = discord.Object(id=822157545622863902)

# @bot.hybrid_command()
# @app_commands.guilds(CSF)
async def help(ctx, *, search: typing.Optional[str] = None):
    region = db.members.find_one({"id": ctx.author.id})["language"]

    color = ctx.guild.me.color
    if color == discord.Color.default():
        color = discord.Color(0xaaffaa)

    if search is not None:
        if len(search.split('.')) == 2:
            search, subcommand = search.split('.')
        else:
            subcommand = None

    def usage(c):
        if dict(c.clean_params) == {}:
            return "Не требует параметров"
        else:
            usage = ""
            c_args = dict(c.clean_params)
            for key in c_args.keys():
                option = False
                types = []
                name = key

                if type(c_args[key].annotation) is typing._GenericAlias:
                    if type(None) in c_args[key].annotation.__args__:
                        option = True
                    types = [i.__name__ for i in c_args[key].annotation.__args__]
                else:
                    types = [c_args[key].annotation.__name__]

                try:
                    types.remove('NoneType')
                except ValueError:
                    pass
                if types[0] == "_empty" or types: types = ["???"]

                if option:
                    if c_args[key].default in (_empty, None):
                        usage += f"({name} [{', '.join(types)}]) "
                    else:
                        usage += f"({name} = {c_args[key].default} [{', '.join(types)}]) "
                else:
                    if c_args[key].default in (_empty, None):
                        usage += f"<{name} [{', '.join(types)}]> "
                    else:
                        usage += f"<{name} = {c_args[key].default} [{', '.join(types)}]> "

            return usage

    if search is None:
        categories = discord.Embed(title="Категории", color=color)
        for cog in bot.cogs.keys():
            categories.add_field(name=cog,
                                 value=bot.cogs[cog].description
                                 if bot.cogs[cog].description != ''
                                 else "Без описания",
                                 inline=False)

        embeds = [categories]

        e = discord.Embed(title="Без категории", color=color)
        for command in [c for c in bot.commands if c.cog is None and not c.hidden]:
            if type(command) == discord.ext.commands.core.Group:
                name = f"■ {translate(command.name, region)}"
            elif type(command) == discord.ext.commands.core.Command:
                name = f"● {translate(command.name, region)}"
            e.add_field(name=name,
                        value=translate(command.brief, region)
                        if command.brief != '' and command.brief is not None
                        else "Без описания",
                        inline=False)
        embeds.append(e)

        for cog in bot.cogs.keys():
            e = discord.Embed(title=cog, description=bot.cogs[cog].description, color=color)

            for command in [c for c in bot.commands if c.cog is bot.cogs[cog] and not c.hidden]:
                if type(command) == discord.ext.commands.core.Group:
                    name = f"■ {translate(command.name, region)}"
                elif type(command) == discord.ext.commands.core.Command:
                    name = f"● {translate(command.name, region)}"
                e.add_field(name=name,
                            value=translate(command.brief, region) if command.brief != '' else "Без описания",
                            inline=False)
            embeds.append(e)
        embeds_ = []

        for i in range(len(embeds)):
            e = embeds[i].to_dict()
            e["description"] = f"`{i + 1}/{len(embeds)}`"
            embeds_.append(discord.Embed.from_dict(e))

        embeds = embeds_

        embeds[0].set_footer(text=f"Для помощи по категориям введите `{ctx.prefix}help <категория>`\n"
                                  f"Для помощи по группам введите `{ctx.prefix}help <группа>`\n"
                                  "Имя категорий всегда с заглавной буквы,в отличии от комманд")
        for e in embeds[1:]:
            e.set_footer(text="● - обычные комманды\n■ - комманды с подпунктами (группы)")

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        await paginator.run(embeds)

    else:
        # Сначала находим категорию
        cog = [cog for cog in bot.cogs if cog == search]
        if cog:
            cog = cog[0]
            e = discord.Embed(title=cog, description=bot.cogs[cog].description, color=color)

            for command in [c for c in bot.commands if c.cog is bot.cogs[cog]]:
                if type(command) == discord.ext.commands.core.Group:
                    name = f"■ {translate(command.name, region)}"
                elif type(command) == discord.ext.commands.core.Command:
                    name = f"● {translate(command.name, region)}"
                e.add_field(name=name,
                            value=translate(command.brief, region) if command.brief != '' else "Без описания",
                            inline=False)

            await ctx.send(embed=e)
        else:
            command = [command for command in bot.commands if command.name == search]
            if command:
                command = command[0]

                # checks = ""
                #
                # for c in  command.checks:
                #     try:
                #         checks += "+" if await c(ctx) else "-"
                #     except:
                #         checks += "+" if c(ctx) else "-"
                #     checks += " " + c.__name__
                #     checks += "\n"
                #
                # if command.cog is not None:
                #     checks = command.cog.cog_check(ctx).__name__ + "\n" + checks
                #     try:
                #         checks = "+ " if await command.cog.cog_check(ctx) else "- " + checks
                #     except:
                #         checks = "+ " if command.cog.cog_check(ctx) else "- " + checks
                #
                # checks = "```diff\n" + checks + "```"
                e = discord.Embed(title=command.name,
                                  description=f"""Другие имена: {', '.join(command.aliases)
                                  if ', '.join(command.aliases) != ''
                                  else 'Отсутствуют'}\n"""
                                              f"Краткое описание: {translate(command.brief, region)}\n"
                                              f"Использование: \n  `{usage(command)}`\n"
                                              f"Описание: \n  {translate(command.description, region)}\n"
                                              f"Родитель: {command.parent.__name__ if command.parent is not None else 'Отсутствует'}\n" 
                                              f"Категория: {command.cog_name if command.cog is not None else 'Отсутствует'}\n"
                                              # f"Чеки: {checks}\n"
                                              f"Спрятан: {command.hidden}\n",
                                  color=color)
                if type(command) == discord.ext.commands.core.Group:
                    if subcommand is None:
                        for subcommand in command.commands:
                            e.add_field(name=subcommand.name, value=subcommand.brief
                                if subcommand.brief is not None and subcommand.brief != ''
                                else "Без описания")
                    else:
                        command = [command for command in command.commands if command.name == subcommand]
                        if command:
                            command = command[0]
                            e = discord.Embed(title=command.name,
                                              description=f"Другие имена: {', '.join(command.aliases)}\n"
                                                          f"Краткое описание: {translate(command.brief, region)}\n"
                                                          f"Использование: \n  `{usage(command)}`\n"
                                                          f"Описание: \n  {translate(command.description, region)}\n"
                                                          f"Родитель: {command.parent if command.parent is not None else 'Отсутствует'}\n"
                                                          f"Категория: {command.cog_name if command.cog is not None else 'Отсутствует'}\n"
                                                          # f"Чеки: {checks}\n"
                                                          f"Спрятан: {command.hidden}\n",
                                              color=color)
                        else:
                            await ctx.send("Субкомманда не найдена")
                await ctx.send(embed=e)
            else:
                await ctx.send("Ничего не найдено")


@bot.command()
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx, count: int):
    count += 1

    while count > 100:
        await ctx.channel.purge(limit=100)
        count -= 100
    await ctx.channel.purge(limit=count)


@bot.group(brief="$commands_HTiP_brief")
async def HTiP(ctx):
    region = ctx.message.author.id
    region = db.members.find_one({"id": region})["language"]

    if ctx.invoked_subcommand is None:
        await ctx.send(translate('$commands_HTiP_subcommand', region))

    abc = str(ctx.message.attachments[0].filename)[-3:]
    if not ctx.message.attachments and abc != 'jpg' and abc != 'png':
        await ctx.send(translate('$commands_HTiP_picNotExists', region))

    else:
        url = ctx.message.attachments[0].url
        filename = ctx.message.attachments[0].filename
        img = requests.get(url)
        img_file = open(filename, 'wb')
        img_file.write(img.content)
        img_file.close()


@HTiP.command(brief="$commands_HTiP_w_brief")
async def w(ctx, *, text: str):
    region = ctx.message.author.id
    region = db.members.find_one({"id": region})["language"]

    if text is None:
        await ctx.send(translate('$commands_HTiP_w_textNotExists', region))
        return None

    if text.split(' ')[-1].startswith('key='):
        key = text.split(' ')[-1][4:]
        text = ' '.join(text.split(' ')[:-1])
    else:
        key = None

    if key is not None:
        text = XOR.char_encode(text, key)

    abc = str(ctx.message.attachments[0].filename)[-3:]
    if not ctx.message.attachments and abc != 'jpg' and abc != 'png':
        await ctx.send(translate('$commands_HTiP_picNotExists', region))

    else:
        url = ctx.message.attachments[0].url
        filename = ctx.message.attachments[0].filename
        img = requests.get(url)
        img_file = open(filename, 'wb')
        img_file.write(img.content)
        img_file.close()

    FFC.write(filename, 'secret.' + abc, text)
    with open('secret.' + abc, 'rb') as f:
        file = discord.File(f)
        await ctx.send(file=file)


@HTiP.command(brief="$commands_HTiP_r_brief")
async def r(ctx, key: str = None):
    region = ctx.message.author.id
    region = db.members.find_one({"id": region})["language"]

    try:
        abc = str(ctx.message.attachments[0].filename)[-3:]
        if not ctx.message.attachments and abc != 'jpg' and abc != 'png':
            await ctx.send(translate('$commands_HTiP_picNotExists', region))
    except IndexError:
        await ctx.send(translate('$commands_HTiP_picNotExists', region))

    else:
        url = ctx.message.attachments[0].url
        filename = ctx.message.attachments[0].filename
        img = requests.get(url)
        img_file = open('C:\\Users\\gleb\\PycharmProjects\\systemnik\\' + filename, 'wb')
        img_file.write(img.content)
        img_file.close()

        secret_text = FFC.read(filename)
        if key is not None:
            secret_text = XOR.char_encode(secret_text, key)
        await ctx.send(secret_text)


@bot.command(name='eval')
@commands.check(is_secret)
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
        'on_message_handler': on_message_handler,
        'get': get
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    try:
        await eval(f"{fn_name}()", env)
    except Exception as e:
        await ctx.message.reply(repr(e))


@bot.command()
@commands.is_owner()
async def change_level(ctx, user: typing.Union[discord.Member, int], level):
    if 'int' in str(type(user)):
        id_ = user
    else:
        id_ = user.id

    if not level in ('secret', 'white', 'gray', 'black'):
        await ctx.message.add_reaction(XX)
        raise TypeError
    db.members.update_one({"id": id_}, {"$set": {"access_level": level}})
    await ctx.message.add_reaction(check_mark)

    await asyncio.sleep(3)
    await ctx.message.delete()


@bot.command()
async def change_lang(ctx, user: typing.Union[discord.Member, int], lang):
    lang = lang.upper()
    if 'int' in str(type(user)):
        id_ = user
    else:
        id_ = user.id

    if not lang in ("RU", "EN"):
        await ctx.message.add_reaction(XX)
        raise TypeError
    db.members.update_one({"id": id_}, {"$set": {"language": lang}})
    await ctx.message.add_reaction(check_mark)

    await asyncio.sleep(3)
    await ctx.message.delete()


@bot.command(aliases=["reload"], brief="Перезагружает бота")
@commands.check(is_secret)
async def reboot(ctx):
    if os.name == 'posix':
        await ctx.message.add_reaction(loading)
        with open('reboot', 'w') as f:
            f.write(f"{ctx.message.channel.id} {ctx.message.id}")
        os.system('pm2 restart Koteika')


@bot.command(brief="Управление консолью")
@commands.check(is_secret)
async def cmd(ctx, *, command):
    try:
        proc = await asyncio.create_subprocess_shell(command,
                                                     shell=True,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     stdin=subprocess.PIPE)
        proc_data = await proc.communicate()
        e = discord.Embed(title="Скрипт завершился без ошибок" if proc_data[1] == b'' else "Ошибка",
                          color=discord.Color.green() if proc_data[1] == b'' else discord.Color.red())
        e.add_field(name="STDOUT", value=f"```{proc_data[0][-994:].decode('utf-8')}```") \
            if proc_data[0] != b'' else None
        e.add_field(name="STDERR", value=f"```{proc_data[1][-994:].decode('utf-8')}```") \
            if proc_data[1] != b'' else None

        await ctx.message.reply(embed=e)
    except Exception as e:
        logger.error(repr(e))


@bot.command(brief="Логи")
@commands.check(is_secret)
async def log(ctx):
    try:
        a = subprocess.check_output('cat /home/pi/Koteika/Cat.log', shell=True)
        await ctx.send('```' + a.decode('utf-8')[-1994:] + '```')
    except:
        a = subprocess.check_output('cat /home/pi/Koteika/Cat.log', shell=True)
        await ctx.send('```' + a.decode('utf-8') + '```')


@bot.command(aliases=["vmute", "v_mute", "v_m", "vm"], brief="Выключает микрфоны всех участников ГК")
@commands.has_guild_permissions(administrator=True)
async def voice_mute(ctx):
    channel = ctx.message.author.voice.channel

    if channel is not None:
        for i in channel.members:
            await i.edit(mute=True)
        await ctx.message.add_reaction(check_mark)

    else:
        await channel.send("Ты не находишься в ГК")
        await ctx.message.add_reaction(XX)

    await asyncio.sleep(3)
    await ctx.message.delete()


@bot.command(aliases=["vunmute", "v_unmute", "v_unm", "vu"], brief="Влючает микрфоны всех участников ГК")
@commands.has_guild_permissions(administrator=True)
async def voice_unmute(ctx):
    channel = ctx.message.author.voice.channel

    if channel is not None:
        for i in channel.members:
            await i.edit(mute=False)
        await ctx.message.add_reaction(check_mark)

    else:
        await channel.send("Ты не находишься в ГК")
        await ctx.message.add_reaction(XX)

    await asyncio.sleep(3)
    await ctx.message.delete()


@bot.command(name="сайт", brief="Выводит сайт котика (не доделан)")
async def page(ctx):
    await ctx.message.delete()
    await ctx.send("https://miyakobot.ru/koteika")


@bot.command(brief="Выводит права участника сервера (по умолчанию - кота)")
async def perms(ctx, user: typing.Union[discord.Member, int] = None):
    if user is None:
        user = ctx.author.id
    elif type(user) == discord.Member:
        user = user.id

    p = {}
    out = ''
    for i in ['create_instant_invite', 'kick_members', 'ban_members', 'administrator', 'manage_channels',
              'manage_guild', 'add_reactions', 'view_audit_log', 'priority_speaker', 'stream', 'read_messages',
              'send_messages', 'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files',
              'read_message_history', 'mention_everyone', 'external_emojis', 'view_guild_insights', 'connect', 'speak',
              'mute_members', 'deafen_members', 'move_members', 'use_voice_activation', 'change_nickname',
              'manage_nicknames', 'manage_roles', 'manage_webhooks', 'manage_emojis']:
        p[i] = False

    perms = ctx.guild.get_member(user).guild_permissions
    for i in iter(perms):
        p[i[0]] = i[1]

    for i in p.keys():
        if p[i]:
            out += '+ '
        else:
            out += '- '
        out += i + '\n'

    await ctx.send('```diff\n' + out + '```')


# @bot.command()
# async def levels(ctx):
#     e = discord.Embed(title="Работяги:")
#     for level in ('secret', 'white', 'gray', 'black'):
#         e.add_field(name=level, value='\n'.join(
#             [i[0] for i in cursor.execute(f'''SELECT name FROM members WHERE access_level="{level}"''').fetchall()]))
#     await ctx.send(embed=e)


@bot.command()
@commands.has_guild_permissions(administrator=True)
async def change_prefix(ctx, prefix):
    prefs[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        dump(prefs, f)


@bot.command()
async def wait(ctx, *, params):
    events = ['typing', 'message', 'member_update']

    params = json.loads(params)
    event = params.pop('event')

    if event in events:
        def check(element):
            out = True

            for param in params.keys():
                if '.' in param:
                    param_ = param.split('.')
                else:
                    param_ = [param]
                for i in param_:
                    if i in dir(element):
                        element = getattr(element, i)
                    else:
                        out = False
                if element != params[param]: out = False

            return out

        await bot.wait_for(event, check=check)
        await ctx.send(ctx.message.author.mention)
    if event == "member_update":
        def check(before, element):
            out = True

            for param in params.keys():
                if '.' in param:
                    param_ = param.split('.')
                else:
                    param_ = [param]
                for i in param_:
                    if i in dir(element):
                        element = getattr(element, i)
                    else:
                        out = False
                if element != params[param]: out = False

            return out

        await bot.wait_for(event, check=check)
        await ctx.send(ctx.message.author.mention)


@logger.catch
def main():
    bot.run(TOKEN)

main()
