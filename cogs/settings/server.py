from discord import TextChannel, app_commands, Interaction
from discord.ext import commands, tasks

from bot import db

import schedule
from loguru import logger
from datetime import datetime

col = db.guild_settings

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class ServerSettings(app_commands.Group, name="настройки_сервера"):
    def add_server_settings(self, server_id: int):
        if not col.find_one({"id": server_id}):
            col.insert_one({
                "id": server_id,
                "levelup": "none",
                "flood_channels": [],
                "commands_channels": [],
                "AFK": {
                    "role": None,
                    "time": -1,
                    "outsaider_help": False,
                    "outsaider_help_time": -1
                },
                "clear_top": {
                    "enable": False,
                    "channel": None,
                    "active_role": None,
                    "voice_active_role": None
                },
                "aux": {
                    "talk": False
                }
            })

    #@app_commands.command()
    #async def обзор(self, inter: Interaction):
    #    await inter.response.send_message("Meow")

    @app_commands.command(name="назначить_флудилкой")
    async def add_flood_channel(self, inter: Interaction, channel: TextChannel = None):
        self.add_server_settings(inter.guild_id)

        if channel is None:
            channel = inter.channel
        
        col.update_one(
            {"id": inter.guild_id},
            {"$push": {"flood_channels": channel.id}}
        )

        await inter.response.send_message(f"Канал {channel.mention} успешно стал каналом для флуда")

    @app_commands.command(name="управление_ответами")
    async def set_aux_talk(self, inter: Interaction, status: bool):
        self.add_server_settings(inter.guild_id)

        col.update_one({'id': inter.guild_id}, {'$set': {'aux.talk': status}})
        if status:
            await inter.response.send_message("Теперь бот будет отвечать")
        else:
            await inter.response.send_message("Бот больше не будет отвечать")

#class NiceName(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot
#
#        schedule.every().day.at("00:00:00").do(self.trigger)
#        self.pending.start()
#
#    @tasks.loop(seconds=1)
#    async def pending(self):
#        #schedule.run_pending()
#        trigger
#
#    def trigger(self):
#        asyncio.new_event_loop().run_untill_complete(clear_top())
#
#    async def clear_top(self):
#        if datetime.now().day == 1:
#            logger.debug("Очистка топа!!!!")
#
#            for data in col.find({"clear_top.enable": True}):
#                server = self.bot.get_guild(data['id'])
#                channel = self.bot.get_channel(data['clear_top']['channel'])
#                active = server.get_member(db.members.find({"guild_stat.822157545622863902": {"$exists": True}}).sort(f"guild_stat.{data['id']}.exp", -1)[0]['id'])
#                active_role = server.get_role(data['clear_top']['active_role'])
#                await active.add_roles(active_role)
#
#                db.members.update_many({}, {"$unset": f"guild_stat.{server_id}"})


async def setup(bot):
    bot.tree.add_command(ServerSettings())
