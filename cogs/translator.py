import discord
from discord import app_commands
from typing import Optional
from loguru import logger
from discord.app_commands import TranslationContextLocation as trans_context

import json


class MeowTranslator(app_commands.Translator):
    async def load(self):
        with open('translations.json', 'r') as f:
            self.translations = json.loads(f.read())

    async def unload(self): pass
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext) -> Optional[str]:
        logger.debug(f"{locale}\t{string.message}")
        if str(locale) == "uk": locale = "ru"   # TODO: make translation for Ukranian
        if str(locale) not in self.translations.keys(): return
        if context.location is trans_context.other:
            if f"{context.data}.{string.message}" in self.translations[str(locale)].keys(): 
                return self.translations[str(locale)][f"{context.data}.{string.message}"]
            elif context.data in self.translations[str(locale)].keys():
                return self.translations[str(locale)][context.data]
            else: return
        if string.message not in self.translations[str(locale)].keys(): return
        return self.translations[str(locale)][string.message]


async def setup(bot):
    await bot.tree.set_translator(MeowTranslator())

