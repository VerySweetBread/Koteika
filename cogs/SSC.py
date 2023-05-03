import asyncio

from discord.ext import commands, tasks
from discord.utils import get
from requests import get
from requests.structures import CaseInsensitiveDict

from re import findall                      # Импортируем библиотеку по работе с регулярными выражениями
from subprocess import check_output         # Импортируем библиотеку по работе с внешними процессами

from json import loads
from cogs.emojis import check_mark, XX
from subprocess import run as cmd
import discord
from discord import app_commands

from loguru import logger

class SSC(commands.Cog, name="SSC"):
    """Управление моей Системой Умной Комнаты Альфа-версия"""

    def __init__(self, bot):
        self.bot = bot
        self.cooler.start()
        logger.debug("Cooler.start()")
        self.last_temp = 0

    def cog_unload(self):
        self.cooler.cancel()

    async def cog_check(self, ctx):
        return ctx.message.author.id in (self.bot.owner_id, 779697451404886016)

    @commands.command(brief="Включает/выключает свет")
    async def light(self, ctx):
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer cvbnmjhgvbnmj"
        get("http://localhost:80/API/light", headers=headers)

        await asyncio.sleep(3)
        await ctx.message.delete()

    @commands.command(brief="Показывает темпераруру",
                      aliases=['temp'])
    async def temperature(self, ctx):
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer cvbnmjhgvbnmj"
        r = get("http://localhost:80/API/temperature", headers=headers)
        j = loads(r.text)
        await ctx.send(f"__DHT__\n"
                       f"Температура: {j['DHT']['temperature']}\n"
                       f"Влажность: {j['DHT']['humidity']}\n"
                       f"__CPU__\n"
                       f"Температура: {j['CPU']['temperature']}")

    @tasks.loop(minutes=1)
    async def cooler(self):
        temp0 = 55
        temp1 = 80
        min_pwm = 125

        temp = get_temp()
        # logger.info(f"Температура процессора: {temp}")

        pwm = (temp-temp0) / (temp1-temp0)
        pwm = int((255 - min_pwm)*pwm + min_pwm)

        if self.last_temp < temp: pwm += 25
        self.last_temp = temp
        # if temp <= 65: pwm += 50

        if pwm < min_pwm: pwm = 0
        if pwm > 255: pwm = 255

        # logger.info(f"Мощность куллера: {pwm} ({int(pwm/256*100)}%)")

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer cvbnmjhgvbnmj"
        get(f"http://localhost/API/cooler/{pwm}", headers=headers)

    @app_commands.command()
    async def host(self, inter):
        await inter.response.send_message(cmd(["neofetch", "--stdout"], capture_output=True).stdout.decode("utf-8"))


    # @tasks.loop(seconds=1)
    # async def open_door(self):
    #     if self.arduino.inWaiting() > 0:
    #         data = self.arduino.readline()
    #         if data == b'door\r\n':
    #             embed = discord.Embed(title="Дверь открыта!", color=discord.Color(0xFF0000))
    #             await get(self.bot.users, id=self.bot.owner_id).send(embed=embed, delete_after=15)
    #         elif data == b'test\r\n':
    #             self.arduino.write(b'2')
    #         else:
    #             await get(self.bot.users, id=self.bot.owner_id).send(data)

    # @tasks.loop(seconds=1)
    # async def alarm(self):
    #     now = datetime.datetime.now()
    #     time = datetime.time(7)
    #     delta = datetime.timedelta(seconds=2)
    #     combine = datetime.datetime.combine(now.date(), time)
    #
    #     if combine-delta <= now <= combine+delta:
    #         await get(self.bot.users, id=self.bot.owner_id).send("!!!")
    #         self.arduino.write(b'1')
    #         await asyncio.sleep(1)
    #         self.arduino.write(b'1')
    #         await asyncio.sleep(1)
    #         self.arduino.write(b'1')

def get_temp():
    temp = check_output(["vcgencmd", "measure_temp"]).decode()  # Выполняем запрос температуры
    temp = float(findall('\d+\.\d+', temp)[
                     0])  # Извлекаем при помощи регулярного выражения значение температуры из строки "temp=47.8'C"
    return (temp)

async def setup(bot):
    await bot.add_cog(SSC(bot))
