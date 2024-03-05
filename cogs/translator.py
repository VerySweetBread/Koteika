import discord
from bot import db
from discord import app_commands
from typing import Optional
from loguru import logger
from discord.app_commands import TranslationContextLocation as trans_context

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

class MeowTranslator(app_commands.Translator):
    async def load(self):
        with open("translations.yaml") as f:
            self.translations = load(f, Loader=Loader)

    def get_key(self, *args):
        key = self.translations
        for arg in args:
            key = key.get(arg, {})
        if key == {}: key = None
        logger.debug(('/'.join(args), key))
        return key


    async def unload(self): del self.translations
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext) -> Optional[str]:
        if context.data is str:
            search_dict = [str(locale), str(context.location.value), context.data, string.message]
        else:
            search_dict = [str(locale), str(context.location.value), string.message]
        data = self.get_key(*search_dict)
        if data:
            return data

        if str(locale) == 'en-US': return
        if str(locale) == 'uk': 
            search_dict[0] = 'ru'
            return self.get_key(*search_dict)
        else:
            search_dict[0] = 'en-US'
            return self.get_key(*search_dict)


async def setup(bot):
    await bot.tree.set_translator(MeowTranslator())

