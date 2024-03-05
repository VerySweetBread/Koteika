import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

from utils.checks import is_white
import asyncio
from utils.emojis import check_mark

from bot import db


class privateChannels(commands.Cog, name="Приватные комнаты"):
    """Работа с приватными комнатами"""

    def __init__(self, bot):
        self.bot = bot
        db.cursor().execute("CREATE TABLE IF NOT EXISTS private_channels (\n"
                            "    guild_id INTEGER NOT NULL               ,\n"
                            "    category_id INTEGER NOT NULL            ,\n"
                            "    main_channel_id INTEGER NOT NULL         \n"
                            ")                                              ")
        db.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        cursor = db.cursor()

        cursor.execute("SELECT category_id FROM private_channels WHERE guild_id = ?", (member.guild.id,))
        private_categories = cursor.fetchall()
        # if (
        #     before.channel and
        #     (await db.private_channels.find_one({'id': before.channel.id})) and
        #     not self.bot.get_channel(before.channel.id)
        # ):
        #     await db.private_channels.delete_one({'id': before.channel.id})

        # if (
        #     before.channel and
        #     not before.channel.members and
        #     not (await db.private_channels.find_one({'id': before.channel.id})) and
        #     (await db.private_channels.find_one({'category_id': before.channel.category_id}))
        # ):
        if before.channel:
            cursor.execute("SELECT main_channel_id FROM private_channels WHERE category_id = ?", (before.channel.category_id,))
            data = cursor.fetchone()
            if data and before.channel.id != data[0]:
                await before.channel.delete()

        # if after.channel and (await db.private_channels.find_one({"id": after.channel.id})):
        if after.channel:
            cursor.execute("SELECT main_channel_id FROM private_channels WHERE category_id = ?", (after.channel.category_id,))
            data = cursor.fetchone()
            if data and after.channel.id == data[0]:
                new_private = await after.channel.category.create_voice_channel(name=member.display_name)

                try:
                    await member.edit(voice_channel=new_private)
                except discord.errors.HTTPException:
                    await new_private.delete()

                try:
                    await new_private.set_permissions(member, manage_channels=True, move_members=True, manage_permissions=True)
                except:
                    pass

        voice = member.guild.me.voice

        if voice and tuple(voice.channel.members) == (member.guild.me,):
            await member.guild.voice_client.disconnect()

    @app_commands.command(description="Присваивает комнату главной")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_private(self, inter: discord.Interaction, channel: discord.VoiceChannel):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM private_channels WHERE category_id = ?", (channel.category.id))
        # if (await db.private_channels.find_one({'id': ctx.author.voice.channel.id})):
        #     await ctx.message.delete()
        #     message = await ctx.send('Канал уже добавлен')
        # else:
        #     await db.private_channels.insert_one({"id": ctx.author.voice.channel.id, 'category_id': ctx.author.voice.channel.category.id})
        #     await ctx.message.add_reaction(check_mark)
        #     message = ctx.message
        if cursor.fetchone():
            await inter.response.send_message("Этот канал уже добавлен или канал является приватным", ephemeral=True)
        else:
            cursor.execute("INSERT INTO private_channels VALUES (?, ?, ?)", (channel.guild.id, channel.category.id, channel.id))
            db.commit()
            await inter.response.send_message("Выполнено", ephemeral=True)

    @commands.command(description="Делает комнату не приватной")
    @app_commands.checks.has_permissions(administrator=True)
    async def unset_private(self, inter: discord.Interaction, channel: discord.VoiceChannel):
        # if ctx.author.voice is not None:
        #     message = await ctx.send("Требуется выйти из ГК")
        #     await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
        #         member == ctx.message.author and after.channel is None)
        #     await message.edit(content="Зайдите в ГК")
        #     await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
        #         member == ctx.message.author and after.channel is not None)
        # else:
        #     message = await ctx.send("Зайдите в ГК")
        #     await self.bot.wait_for("voice_state_update", check=lambda member, _, after: \
        #         member == ctx.message.author and after.channel is not None)
        # if (await db.private_channels.find_one({'id': ctx.author.voice.channel.id})):
        #     await db.private_channels.delete_one({"id": ctx.author.voice.channel.id})
        #     await ctx.message.add_reaction(check_mark)
        # else:
        #     await message.edit(content='Этот канал не является приватным')
        #
        # await asyncio.sleep(3)
        # await ctx.message.delete()
        # await message.delete()
        cursor.execute("SELECT * FROM private_channels WHERE main_channel_id = ?", (channel.id,))
        if not cursor.fetchone():
            await inter.response.send_message("Этот канал не является приватным", ephemeral=True)
        else:
            cursor.execute("DELETE FROM private_channels WHERE main_channel_id = ?", (channel.id,))
            db.commit()
            await inter.response.send_message("Выполнено", ephemeral=True)


async def setup(bot):
    await bot.add_cog(privateChannels(bot))
