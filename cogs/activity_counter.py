import discord
import schedule
from discord import app_commands
from discord.ext import commands, tasks
from bot import db
from datetime import datetime, timedelta, timezone
from matplotlib import pyplot as plt
from matplotlib import ticker, markers
from loguru import logger


class ActiveCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        plt.style.use(['default', "dark.mplstyle", ])
        
        self.daysoftheweek = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

        for server in bot.guilds:
            self.add_server(server.id)

    def add_server(self, server_id: int):
        if not db.history.find_one({"type": "server", "id": server_id}):
            db.history.insert_one({
                "type": "server",
                "id": server_id,
                "history": {
                    day: {
                        str(i): [] for i in range(24)
                    } for day in self.daysoftheweek
                },
                "current":   {str(i): 0  for i in range(24)},
                "yesterday": {str(i): 0  for i in range(24)},
                "avarage":   {str(i): [] for i in range(24)}
            })

    # TODO: добавить сервер, если кот зашел на новый сервак

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None: return

        hour = message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None).hour
        db.history.update_one(
            {"type": "server", "id": message.guild.id},
            {"$inc": {f"current.{hour}": 1}}
        )

    @app_commands.command()
    async def activity(self, inter):
        async def get_string(inter, string: str) -> str:
            data = await self.bot.tree.translator.translate(
                app_commands.locale_str(string),
                inter.locale,
                app_commands.TranslationContext(
                    app_commands.TranslationContextLocation.other,
                    "activity"
                )
            )
            logger.debug(data)

            if data is None: return string
            return data

        day = datetime.now().weekday()
        fig, ax = plt.subplots(figsize=(8, 5))

        server_data = db.history.find_one({"type": "server", "id": inter.guild_id})

        if server_data is None:
            await inter.response.send_message("Недостаточно данных! Попробуйте завтра")
            return

        data = server_data['avarage']
        vals = list(map(lambda k: sum(data[k]) / len(data[k]) if len(data[k]) != 0 else 0, data.keys()))
        labels = list(map(int, data.keys()))
        ax.bar(labels, vals, width=.9, label=await get_string(inter, "Avarage"))

        vals = list(map(lambda k: max(data[k]) if len(data[k]) != 0 else 0, data.keys()))
        ax.plot(labels, vals, label=await get_string(inter, "Max"), linestyle='', marker="_", markersize=20)

        data = server_data['history'][self.daysoftheweek[day]]
        vals = list(map(lambda k: sum(data[k]) / len(data[k]) if len(data[k]) != 0 else 0, data.keys()))
        labels = list(map(int, data.keys()))
        ax.bar(labels, vals, width=.6, label=await get_string(inter, "On this day\nof the week"))

        data = server_data['yesterday']
        vals = [data[k] for k in data.keys()]
        labels = [int(i) for i in data.keys()]
        ax.bar(labels, vals, width = .4, hatch='x', label=await get_string(inter, "Yesterday"))

        data = server_data['current']
        vals = [data[k] for k in data.keys()]
        labels = [int(i) for i in data.keys()]
        ax.bar(labels, vals, width = .4, label=await get_string(inter, "Today"))

        now = datetime.now()
        ax.axvline(now.hour+(now.minute/60)-0.5, color='dimgrey')


        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_minor_formatter(ticker.ScalarFormatter())
        ax.tick_params(axis='x', which='minor', labelsize=8)
        ax.legend(loc='upper left')
        ax.grid(axis='y')
        ax.set_axisbelow(True)
        ax.set_xlabel(await get_string(inter, 'Hours'))
        ax.set_ylabel(await get_string(inter, 'Experience'))
        ax.set_xlim(-0.5, 23.5)

        ax.legend().get_frame().set_boxstyle('Round', pad=0.2, rounding_size=1)
        ax.legend().get_frame().set_linewidth(0.0)
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        fig.savefig('temp.png')
        with open('temp.png', 'rb') as f:
          f = discord.File(f)
          await inter.response.send_message(file=f)

async def setup(bot):
    await bot.add_cog(ActiveCount(bot))
