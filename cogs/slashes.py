import discord

from discord.ext.commands import Cog
from discord.app_commands import Choice
from discord    import app_commands
from os         import listdir, stat
from os.path    import join
from random     import choice
from requests   import get
from json       import loads
from loguru     import logger


class Slashes(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    #@logger.catch
    async def error(self, inter):
        0/0

    
    @app_commands.command(description="About this bot")
    async def about(self, inter):
        info_text = await self.bot.tree.translator.translate(
            app_commands.locale_str("info"),
            inter.locale,
            app_commands.TranslationContext(
                app_commands.TranslationContextLocation.other,
                "info"
            )
        )
        if info_text is None:
            info_text = "Meow! I'm ~~another~~ discord bot ~~that will"\
                "once again try to take over the world~~.\n"\
                "Creator: Сладкий Хлеб#1199\n"\
                "Written on: Discord.py\n"\
                "Host: </host:981229566804774944>"

        await inter.response.send_message(info_text, ephemeral=True)

    @app_commands.command(description="Random hentai", nsfw=True)
    @app_commands.choices(format = [
        Choice(name="Image",    value='jpg'),
        Choice(name="GIF",      value='gif'),
        Choice(name="Video",    value='mp4')
    ])
    async def hentai(self, inter, format: Choice['str'] = None):
        if format is None:
            format = 'jpg'
        else:
            format = format.value
        dir = "/media/pi/hentai"
        await inter.response.defer()
        filename = choice([i for i in listdir(dir) if i.endswith(format)])
        if stat(join(dir, filename)).st_size > 8*1024*1024:
            await inter.edit_original_response(content=f"https://miyakobot.ru/hentai/{filename}")
        else:
            with open(join(dir, filename), 'rb') as f:
                await inter.edit_original_response(attachments=[discord.File(f)])

    @app_commands.command(description="Получение данных о хентай-манге из nhentai.xxx", nsfw=True)
    async def nhentai(self, inter, hentai_id: int):
        data = loads(get(f"http://130.61.95.102:5000/{hentai_id}").text)
        e = discord.Embed(
                title=data['title'], 
                description=f"{data['description']} \n`{data['id']}`",
                url=f"https://nhentai.xxx/g/{hentai_id}"
        )
        e.set_image(url=f"http://130.61.95.102:5000/cover/{data['cover']}")
        data = data['data']
        if 'parodies' in data.keys():
            e.add_field(name="Пародии на",  value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['parodies']),      inline=False)
        if 'characters' in data.keys():
            e.add_field(name="Персонажи",   value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['characters']),    inline=False)
        if 'tags' in data.keys():
            e.add_field(name="Тэги",        value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['tags']),          inline=False)
        if 'artists' in data.keys():
            e.add_field(name="Художники",   value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['artists']),       inline=False)
        if 'groups' in data.keys():
            e.add_field(name="Группы",      value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['groups']),        inline=False)
        if 'languages' in data.keys():
            e.add_field(name="Языки",           value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['languages']),     inline=False)
        if 'categories' in data.keys():
            e.add_field(name="Категории",       value="\n".join(f"{tag['name']}\|{tag['count']}" for tag in data['categories']),    inline=False)

        e.add_field(name="Страниц",     value=data['pages'])
        e.add_field(name="Загружено",   value=data['uploaded'])

        await inter.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Slashes(bot))
