from discord import app_commands, Interaction

class Tamagochi(app_commands.Group):
    @app_commands.command()
    async def test(self, inter: Interaction):
        await inter.response.send_message("Meow")

async def setup(bot):
    bot.tree.add_command(Tamagochi(name="tamagochi", guild_only=True))
