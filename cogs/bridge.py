import discord
import requests
import uuid
import aiohttp
import asyncio

from discord.ext import commands

class Bridge(commands.Cog):
    def __init__(self): 
        self.base_url = "https://www.guilded.gg/api"
        self.session = aiohttp.ClientSession()

        asyncio.create_task(self.meow())
    
    async def meow(self):
        await self.session.post(f"{self.base_url}/login", json={"email": "miyako@miyakobot.ru", "password": "miyakotb"})

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None: return
        if message.guild.id != 822157545622863902: return

        if message.channel.id == 822157545622863905:
            channel_id = "e11508c9-b817-404d-8ac4-22ff288f8f48"
        elif message.channel.id == 822582629390876762:
            channel_id = "5b228995-ceb6-442a-b65e-162a797b5253"
        elif message.channel.id == 864989115242250280:
            channel_id = "7cd64e7d-2747-4cea-90a5-3c7b57c2b895"
        elif message.channel.id == 977920558140379176:
                channel_id = "15404706-85b8-45a0-b969-57394953917c"
        else:
            return

        #await message.channel.send(f"{self.base_url}/channels/{channel_id}/messages")

        nick = message.author.nick
        if nick is None:
            nick = message.author.name

        json = {
                "messageId": str(uuid.uuid4()),
                "content": {                                                       
                    "object": "value",
                    "document": {     
                        "object": "document",
                        "data": {},
                        "nodes": [{   
                            "object": "block",
                            "type": "paragraph",
                            "nodes": [{
                                "object": "text",
                                "leaves": [{
                                    "object": "leaf",
                                    "text": nick,
                                        "marks": [{
                                            "data": {},
                                            "object": "mark",
                                            "type": "inline-code-v2"
                                        }]
                                }]
                            }]
                        }, {       
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [{       
                                "object": "text",
                                "leaves": [{
                                    "object": "leaf",
                                    "text": message.content,   
                                    "marks": []   
                                }]  
                            }]  
                        }]  
                    }  
                }
            }

        await self.session.post(f"{self.base_url}/channels/{channel_id}/messages", json=json)

async def setup(bot):
    await bot.add_cog(Bridge())
           

