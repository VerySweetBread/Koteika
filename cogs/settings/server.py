import discord
from discord import TextChannel, app_commands, Interaction
from discord.ext import commands, tasks

from bot import db

import schedule
from loguru import logger
from datetime import datetime

import requests
from io import BytesIO
from hashlib import sha256
from os.path import splitext

col = db.guild_settings

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class ServerSettings(app_commands.Group, name="настройки_сервера"):
    def __init__(self, bot):
        super().__init__()
        bot.add_listener(self.bayans_listener, name='on_message')

    async def add_server_settings(self, server_id: int):
        if not (await col.find_one({"id": server_id})):
            await col.insert_one({
                "id": server_id,
                'type': 'general',
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
        await self.add_server_settings(inter.guild_id)

        if channel is None:
            channel = inter.channel
        
        await col.update_one(
            {"id": inter.guild_id},
            {"$push": {"flood_channels": channel.id}}
        )

        await inter.response.send_message(f"Канал {channel.mention} успешно стал каналом для флуда")

    @app_commands.command(name="управление_ответами")
    async def set_aux_talk(self, inter: Interaction, status: bool):
        await self.add_server_settings(inter.guild_id)

        await col.update_one({'id': inter.guild_id}, {'$set': {'aux.talk': status}})
        if status:
            await inter.response.send_message("Теперь бот будет отвечать")
        else:
            await inter.response.send_message("Бот больше не будет отвечать")

    @app_commands.command()
    async def check_bayans(self, itr: Interaction, channel: TextChannel = None):
        if not channel:
            channel = itr.channel

        search_dict = {'id': itr.guild_id, 'type': 'bayans', 'channel': channel.id}

        if (await col.find_one(search_dict)):
            await col.delete_one(search_dict)
            await db.bayans.delete_many({'channel': channel.id})
            await itr.response.send_message(f"В {channel.mention} больше не стоит проверка на баяны", delete_after=15)
        else:
            await col.insert_one(search_dict)
            string = "Обработка всех сообщений... Это может занять несколько лет\n{:>4} сообщений обработано"
            await itr.response.send_message("Обработка всех сообщений... Это может занять несколько лет")

            i = 0
            async for mes in channel.history(limit=None):
                if i%1000 == 0:
                    await itr.edit_original_response(content=string.format(i))

                for attachment in filter(lambda m: splitext(m.filename)[1] in ('.png', '.jpg'), mes.attachments):
                    img = requests.get(attachment.url)
                    with BytesIO(img.content) as buffer:
                        hash0 = sha256(buffer.getbuffer()).hexdigest()
                    if not (await db.bayans.find_one({'id': mes.guild.id, 'channel': mes.channel.id, 'sha256': hash0})):
                        await db.bayans.insert_one({'id': mes.guild.id, 'channel': mes.channel.id, 'message': mes.id, 'sha256': hash0, 'index': i})

                i += 1

            await itr.edit_original_response(content=f"Теперь в {channel.mention} стоит проверка на баяны. Сообщений обработано: {i}", delete_after=15)

    async def bayans_listener(self, message: discord.Message):
        if message.attachments and (await col.find_one({'id': message.guild.id, 'type': 'bayans', 'channel': message.channel.id})):
            out = []

            for i, attachment in enumerate(filter(lambda m: splitext(m.filename)[1] in ('.png', '.jpg'), message.attachments)):
                img = requests.get(attachment.url)
                with BytesIO(img.content) as buffer:
                    hash0 = sha256(buffer.getbuffer()).hexdigest()
                if (a := await db.bayans.find_one({'id': message.guild.id, 'channel': message.channel.id, 'sha256': hash0})):
                    out.append(f"Найдено {i+1} изображение в https://discord.com/channels/{a['id']}/{a['channel']}/{a['message']} /{a['index']+1} (SHA256: `{hash0}`)")
                else:
                    await db.bayans.insert_one({'id': message.guild.id, 'channel': message.channel.id, 'message': message.id, 'sha256': hash0, 'index': i})
            
            if out:
                await message.reply('\n'.join(out))



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
    bot.tree.add_command(ServerSettings(bot))
