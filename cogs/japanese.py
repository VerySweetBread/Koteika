import discord
import sqlite3
import romkan

from discord import app_commands
from discord.ext import commands

class Group(app_commands.Group):
    def __init__(self, db, name):
        self.db = db
        super().__init__(name=name)

    def flot_parser(self, string: str) -> str:
        output = ""
        counter = 1

#        for marpheme in string:
#            if len(marpheme) == 0:
#                continue
#            elif marpheme[0] == '$':
#                continue
#            elif marpheme[0] == '&':
#                output += f" {counter}. "
#                counter += 1
#                if len(marpheme) == 1: continue
#                if marpheme[1] == '*':
#                    if marpheme[1:] == "3":
#                        output += "〜の"
#            elif marpheme[0] == '@':
#                if marpheme[1:] == "3":
#                    output += " *и и.п.*"
#            elif marpheme[0] == ';':
#                output += '; '
#            elif marpheme[0] == ',':
#                output += ', '
#            else:
#                output += marpheme

        print(string)
        i = 0

        while i < len(string):
            char = string[i]
            if char == '&':
                output += f" {counter}. "
                counter += 1 
            elif char == ';':
                output += "; "
            elif char == ',':
                output += ', '
            elif char == '(':
                output += ' ('
            elif char in ('\\', '$'):
                i += 1
                continue
            elif char == '*':
                number = ''

                if string[i+1] == '*':
                    i += 2
                    while string[i].isdigit():
                        number += string[i]
                        i += 1
                    i -= 1
                    if number == '2':
                        output += "〜のある"
                else:
                    i += 1
                    while string[i].isdigit():
                        number += string[i]
                        i += 1
                    i -= 1
                    if number == '2':
                        output += "〜な"
                    elif number == "3":
                        output += "〜の"
                    elif number == '7':
                        output += "〜たる"

            elif char == '@':
                number = ''
                i += 1
                while string[i].isdigit():
                    number += string[i]
                    i += 1
                i -= 1
                print(number)
                if number == "3":
                    output += " *и т.п.*"

            else:
                output += char

            i += 1


        return output

    @app_commands.command(name="копирайты")
    async def copyrights(self, inter):
        await inter.response.send_message("Эта функция основана на базе "\
            "данных проекта Яркси (http://yarxi.ru/)", ephemeral=True)

    @app_commands.command(name="поиск_кандзи")
    @app_commands.describe(kanji="Кандзи, который надо найти")
    async def kanji_search(self, inter, kanji: str):
        kanji = ord(kanji[0])
        data = self.db.execute(f"SELECT Nomer, RusNick, Onyomi, Kunyomi, Russian FROM Kanji WHERE Uncd = {kanji}").fetchall()[0]
        await inter.response.send_message(data)

    @app_commands.command(name="поиск_слов")
    @app_commands.rename(meaning="значение", pronounsing="произношение")
    @app_commands.describe(pronounsing="ТОЛЬКО НА РОМАНДЗИ")
    async def word_search(self, inter, meaning: str=None, pronounsing: str=None):
        if meaning is None and pronounsing is None:
            await inter.response.send_message("Нельзя просто так без всего найти слово")
            return
        if meaning is None:
            searcher = f"{pronounsing}%"
        elif pronounsing is None:
            searcher = f"%{meaning}%"
        predata = self.db.execute(f"SELECT K1, K2, K3, K4, Kana, Reading, Russian From Tango WHERE Russian Like '{searcher}'").fetchall()[:10]
        data = []
        for word in predata:
            kanjis = []
            kana = ""
            number = ""
            for K in word[:4]:
                if K == 0: break
                kanjis.append( chr(self.db.execute(f"SELECT Uncd FROM Kanji WHERE Nomer = {K}").fetchone()[0]) )
            for char in word[4]:
                if char.isdigit():
                    if kana != "":
                        number = int(number)
                        if kana.startswith('^'):
                            kana = romkan.to_katakana(kana[1:])
                        else:
                            kana = romkan.to_hiragana(kana)
                        kanjis.insert(number, kana)
                        number = kana = ""
                       
                    number += char
                else:
                    kana += char
            
            if number != "":
                number = int(number)
                if kana.startswith('^'):
                    kana = romkan.to_katakana(kana[1:])
                else:
                    kana = romkan.to_hiragana(kana)
                kanjis.insert(number, kana)

            print('!!', word[5])
            data.append(f"**{''.join(kanjis)}** [{romkan.to_hiragana(word[5])}] {self.flot_parser(word[6])}")
        if data:
            await inter.response.send_message("\n".join(data))
        else:
            await inter.response.send_message("Ничего не нашла")



class Japanese(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.sqlite_connection = sqlite3.connect('yarxi.db')
        cursor = self.sqlite_connection.cursor()
        self.bot.tree.add_command(Group(db=cursor, name="яп-словарь"))

    async def cog_unload(self):
        self.sqlite_connection.close()
        self.bot.tree.remove_command("яп-ловарь")

    
async def setup(bot):
    await bot.add_cog(Japanese(bot))

