import discord
import schedule
from discord import app_commands
from discord.ext import commands, tasks
from bot import db
from datetime import datetime, timedelta, timezone
from matplotlib import pyplot as plt
from matplotlib import ticker, markers
from loguru import logger
from asyncio import run_coroutine_threadsafe
from utils.translate import get_text

class ActiveCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        plt.style.use(['default', "dark.mplstyle", ])
        
        self.daysoftheweek = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

        db.cursor().execute("CREATE TABLE IF NOT EXISTS history_guilds (\n"
                            "    id INTEGER                            ,\n"
                            "    time TIMESTAMP                        ,\n"
                            "    msgs INTEGER                          ,\n"
                            "    day_of_week INTEGER                    \n"
                            ")                                            ")
        db.commit()


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None: return

        mdt = message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
        year = mdt.year
        month = mdt.month
        day = mdt.day
        hour = mdt.hour
        time = datetime(year, month, day, hour)
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM history_guilds WHERE id = ? AND time = ?", (message.guild.id, time))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO history_guilds VALUES (?, ?, 1, ?)", (message.guild.id, time, mdt.weekday()))
        else:
            cursor.execute("UPDATE history_guilds SET msgs = msgs + 1 WHERE id = ? AND time = ?", (message.guild.id, time))
        db.commit()

    # @app_commands.command()
    # async def activity(self, inter):
    #     day = datetime.now().weekday()
    #     fig, ax = plt.subplots(figsize=(8, 5))
    #
    #     cursor = db.cursor()
    #     cursor.execute("SELECT * FROM history_guilds WHERE id = ?", (inter.guild_id,))
    #     server_data = cursor.fetchall()
    #     
    #     #await db.history.find_one({"type": "server", "id": inter.guild_id})
    #
    #     if not server_data:
    #         await inter.response.send_message("Недостаточно данных! Попробуйте завтра")
    #         return
    #
    #     # data = server_data['avarage']
    #     # data = sum([i[2] for i in server_data]) / len(server_data)
    #     # data = [ for i in ]
    #     vals = list(map(lambda k: sum(data[k]) / len(data[k]) if len(data[k]) != 0 else 0, data.keys()))
    #     labels = list(map(int, data.keys()))
    #     ax.bar(labels, vals, width=.9, label=await get_text(inter, "Avarage"))
    #
    #     vals = list(map(lambda k: max(data[k]) if len(data[k]) != 0 else 0, data.keys()))
    #     ax.plot(labels, vals, label=await get_text(inter, "Max"), linestyle='', marker="_", markersize=20)
    #
    #     data = server_data['history'][self.daysoftheweek[day]]
    #     vals = list(map(lambda k: sum(data[k]) / len(data[k]) if len(data[k]) != 0 else 0, data.keys()))
    #     labels = list(map(int, data.keys()))
    #     ax.bar(labels, vals, width=.6, label=await get_text(inter, "On this day\nof the week"))
    #
    #     data = server_data['yesterday']
    #     vals = [data[k] for k in data.keys()]
    #     labels = [int(i) for i in data.keys()]
    #     ax.bar(labels, vals, width = .4, hatch='x', label=await get_text(inter, "Yesterday"))
    #
    #     data = server_data['current']
    #     vals = [data[k] for k in data.keys()]
    #     labels = [int(i) for i in data.keys()]
    #     ax.bar(labels, vals, width = .4, label=await get_text(inter, "Today"))
    #
    #     now = datetime.now()
    #     ax.axvline(now.hour+(now.minute/60)-0.5, color='dimgrey')
    #
    #
    #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    #     ax.xaxis.set_minor_formatter(ticker.ScalarFormatter())
    #     ax.tick_params(axis='x', which='minor', labelsize=8)
    #     ax.legend(loc='upper left')
    #     ax.grid(axis='y')
    #     ax.set_axisbelow(True)
    #     ax.set_xlabel(await get_text(inter, 'Hours'))
    #     ax.set_ylabel(await get_text(inter, 'Experience'))
    #     ax.set_xlim(-0.5, 23.5)
    #
    #     ax.legend().get_frame().set_boxstyle('Round', pad=0.2, rounding_size=1)
    #     ax.legend().get_frame().set_linewidth(0.0)
    #     ax.xaxis.set_ticks_position('none')
    #     ax.yaxis.set_ticks_position('none')
    #
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.spines['bottom'].set_visible(False)
    #     ax.spines['left'].set_visible(False)
    #
    #     fig.savefig('temp.png')
    #     with open('temp.png', 'rb') as f:
    #       f = discord.File(f)
    #       await inter.response.send_message(file=f)

async def setup(bot):
    await bot.add_cog(ActiveCount(bot))
