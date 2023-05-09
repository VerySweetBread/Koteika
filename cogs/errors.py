import discord
from discord.ext    import commands
from loguru         import logger
from traceback      import print_tb

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Загружено")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        send_help = (commands.TooManyArguments, commands.UserInputError)

        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Отсутствует аргумент `{error.param.name}` типа `{error.param.converter.__name__}`')
        elif isinstance(error, send_help):
            await ctx.send(f'Неправильные аргументы. Для справки, обратись к `{ctx.clean_prefix}help`')
            logger.debug(error.message)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"У бота нет прав на выполнение этой команды. Требуемые права: ```{chr(10).join(error.missing_permissions)}```")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f'Нет прав на выполнение этой комманды. Требуемые права: ```{chr(10).join(error.missing_permissions)}```')
        elif isinstance(error, commands.NotOwner):
            await ctx.send('Очевидно же, что только для создателя бота')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Команда недоступна')
        else:
            logger.debug(error)
            logger.error(print_tb(error))
                    # missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            # if len(missing) > 2:
            #     fmt = '{}, и {}'.format("**, **".join(missing[:-1]), missing[-1])
            # else:
            #     fmt = ' и '.join(missing)
            # _message = 'Мне требуются эти права для выполнения операции: **{}**'.format(fmt)
            # await ctx.send(_message)
        #if type(error) == discord.ext.commands.errors.CommandInvokeError or \
        #        type(error.original) == discord.errors.Forbidden or \
        #        error.original.text == "Missing Permissions":
        #    logger.debug(7)
            # missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            # if len(missing) > 2:
            #     fmt = '{}, и {}'.format("**, **".join(missing[:-1]), missing[-1])
            # else:
            #     fmt = ' и '.join(missing)
            # _message = 'Вам требуются эти права для выполнения операции: **{}**'.format(fmt)
            # await ctx.send(_message)
            await ctx.send(error)


async def setup(bot):
    await bot.add_cog(Errors(bot))
