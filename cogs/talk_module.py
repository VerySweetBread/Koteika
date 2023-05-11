import json
import os
import re
from random import randint, choice

import Levenshtein
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import locale_str as _T
from cogs.checks import is_secret

from bot import db

meow = ['Мяу', '?', ':Р', ':3', '^___^', '(o･ω･o)', '(≧◡≦)']

vase_error = ['По техническим причинам падение вазы невозможно по причинам '
              'отсутствия этих самых ваз\n'
              'Обратитесь к специализированному сотруднику для пополнения '
              'ресурсов. __Спасибо за понимание__',

              'Сотрудники Лаборатории Aperture Science обеспокоены частым разрушением '
              'важного и дорогого лабораторного оборудования, из-за чего на это '
              'был установлен запрет\n'
              'Обратитесь к специализированному сотруднику для снятия '
              'запрета. __Спасибо за понимание__']


class TalkModule(commands.Cog, name="Общение"):
    """Работа с разговорным модулем кота"""

    def __init__(self, bot):
        self.bot = bot
        self.unknown_phrases = []
        if os.path.exists('speak_data.json'):
            with open('speak_data.json', 'r') as f:
                self.data = json.load(f)
        else:
            self.data = [[['привет', 'здаров', 'приветушки'], ['Привет', 'Дароу', 'Мяу', ':)']]]

    @commands.Cog.listener()
    async def on_message(self, message):
        if db.guild_settings.find_one({'id': message.guild.id}) is None: return
        if message.author.name != 'Котейка' and db.guild_settings.find_one({"id": message.guild.id})['aux']['talk']:
            try:
                pattern = re.compile(
                    r'(^|[^а-яА-ЯЁёa-zA-Z]|[,.])((ко(т((ейк)|(ик)|(ан)|([её]нок)|(я[рт]))?|(шак)))([иаыуэя]|(ов)|(ом))?)([^а-яА-ЯЁёa-zA-Z]|$)')
                if pattern.search(message.content.lower()):
                    rand_meow = meow[randint(0, len(meow) - 1)]
                    if False: pass  # rand_meow == '\*Роняет вазу\*':
                    #     try:
                    #         if self.data['vase'] <= 0:
                    #             await message.channel.send(vase_error[randint(0, len(vase_error) - 1)])
                    #             self.data['vase'] = 0
                    #         else:
                    #             await message.channel.send(rand_meow)
                    #             self.data['vase'] -= 1
                    #     except IndexError:
                    #         self.data['vasa'] = 10
                    else:
                        sended = False
                        max_con = 0
                        right_answer = ''
                        i = pattern.search(message.content.lower()).group(0)

                        text = message.content.lower().replace(i, '')
                        if text.startswith(','):
                            text = text[1:]
                        if text.startswith(' '):
                            text = text[1:]
                        text = text.replace('<@>', '')
                        if len(text) >= 3:
                            for group in self.data:
                                # print(group)
                                for known_pharase in group[0]:
                                    # print(known_pharase)
                                    con = Levenshtein.ratio(known_pharase, text)
                                    # print(con)
                                    if con >= 0.65:
                                        if max_con < con:
                                            max_con = con
                                            right_answer = choice(self.data[self.data.index(group)][1])

                                        sended = True

                        if not sended:
                            await message.channel.send(choice(meow))
                            text = message.content.lower().replace(i, '')
                            if text.startswith(','):
                                text = text[1:]
                            if text.startswith(' '):
                                text = text[1:]
                            text = text.replace('<@>', '')
                            if len(text) >= 3:
                                self.unknown_phrases.append(text)
                        else:
                            await message.reply(right_answer)
            except Exception as e:
                print(repr(e))

    @commands.command(brief="Выводит список неизвестных фраз",
                      help="Если кот найдет сообщение, в котором содержится слово \"кот\" (неважно какого "
                           "вида/числа/рода) он попытается на него ответить. Если в базе нет нужного ответа, то кот"
                           "положит сообщение в этот список")
    @commands.check(is_secret)
    async def up(self, ctx):
        if len(self.unknown_phrases) <= 10:
            e = discord.Embed(title="Неизвестные фразы:",
                              description='\n'.join([f"{self.unknown_phrases.index(el) + 1}. {el}"
                                                     for el in self.unknown_phrases]))
        else:
            e = discord.Embed(title="Неизвестные фразы:",
                              description='\n'.join(
                                  [f"{len(self.unknown_phrases) - 10 + i}. {self.unknown_phrases[-10 + i]}"
                                   for i in range(10)]))
        await ctx.send(embed=e)

    @commands.command(brief="Вносит фразу в список неизвестних для дальнейшего обучения")
    @commands.check(is_secret)
    async def down(self, ctx, phrase):
        self.unknown_phrases.append(phrase)

    @commands.command(brief="Обучение коты разговору с жалкими человеками",
                      help="На одну неизвестную фразу может приходиться от одного до нескольких ответов.\n"
                           "Кот будет по одному писать неизвестную фразу и ждать минуту\n"
                           "Для ввода нескольких ответов напиши `+`, а потом по одной пиши ответы. После ввода всех"
                           "ответов напиши `stop`\n"
                           "`cancel` для отмены обучения\n"
                           "`next` для пропуска и удаления вопроса из списка\n"
                           "`pass` для пропуска \"на потом\"\n")
    @commands.check(is_secret)
    async def teach(self, ctx):
        t_author = ctx.message.author
        t_channel = ctx.message.channel
        pharases = tuple(self.unknown_phrases)

        def check(m):
            return (m.author == t_author) and (m.channel == t_channel)

        for phrase in phrases:
            await ctx.send(phrase)

            try:
                answer = await self.bot.wait_for('message', timeout=60.0, check=check)
            except:
                await ctx.send("Обучение прервано. Сработал таймаут на минуту")

            if answer.content.lower() == 'cancel':
                break

            elif answer.content.lower() == 'next':
                del self.unknown_phrases[self.unknown_phrases.index(phrase)]
                continue

            elif answer.content.lower() == 'pass':
                continue

            elif answer.content.lower() == '+':
                await ctx.send('OK')
                id = len(self.data)
                self.data.append([[phrase], []])
                while 1:
                    answerInCycle = await self.bot.wait_for('message', timeout=60.0, check=check)
                    if answerInCycle.content.lower() == 'cancel':
                        break
                    elif answerInCycle.content.lower() == 'stop':
                        del self.unknown_phrases[self.unknown_phrases.index(phrase)]
                        break
                    else:
                        self.data[id][1].append(answerInCycle.content.replace("\'", "\\'"))

                with open('speak_data.json', 'w') as f:
                    json.dump(self.data, f)
                await ctx.send('Сохранено')
                continue

            else:
                self.data.append([[phrase], [answer.content]])

            with open('speak_data.json', 'w') as f:
                json.dump(self.data, f)
            await ctx.send('Сохранено')

        await ctx.send('Неизвестных фраз нет')

    @commands.command(name='del', brief="Удаляет элемент разговорного-БД кота")
    @commands.check(is_secret)
    async def del_f(self, ctx, q, *, a: int = None):
        if a is None:
            del self.data[q]
        else:
            del self.data[q][a]

        with open('speak_data.json', 'w') as f:
            json.dump(self.data, f)
        await ctx.send('Сохранено')

    @commands.command(brief="Выводит сайт с базой данных кота")
    @commands.check(is_secret)
    async def knowledge(self, ctx):
        await ctx.send('https://miyakobot.ru')

    @app_commands.command()
    async def meow(self, inter):
        await inter.response.send_message("Meow")

    @app_commands.command(name=_T("cats"))
    async def cats(self, inter):
        await inter.response.send_message(_T("are cutes"))

async def setup(bot):
    await bot.add_cog(TalkModule(bot))
