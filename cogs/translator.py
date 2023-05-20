import discord
from bot import db
from discord import app_commands
from typing import Optional
from loguru import logger
from discord.app_commands import TranslationContextLocation as trans_context

import json


class MeowTranslator(app_commands.Translator):
    async def load(self):
        with open('translations.json', 'r') as f:
            data = json.loads(f.read())
            self.db = db.translation
            await self.db.delete_many({})
            for locale in data.keys():
                logger.debug(locale)
                for type_ in data[locale].keys():
                    logger.debug('\t'+type_)
                    for key in data[locale][type_].keys():
                        logger.debug('\t\t'+key)
                        translate = data[locale][type_][key]
                        if type(translate) is dict:
                            for tr in translate.keys():
                                logger.debug('\t\t\t'+tr)
                                await self.db.insert_one({'locale': locale, 'type': int(type_), 'context': key, 'string': tr, 'translate': translate[tr]})
                        else:
                            logger.debug('\t\t  '+translate)
                            await self.db.insert_one({'locale': locale, 'type': int(type_), 'string': key, 'translate': translate})


    async def unload(self): pass
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext) -> Optional[str]:
        if context.data is str:
            search_dict = {'locale': str(locale), 'type': context.location.value, 'context': context.data, 'string': string.message}
        else:
            search_dict = {'locale': str(locale), 'type': context.location.value, 'string': string.message}
        data = await self.db.find_one(search_dict)
        if data:
            return data['translate']

        if str(locale) == 'en-US': return
        if str(locale) == 'uk': search_dict['locale'] = 'ru'
        else: search_dict['locale'] = 'en-US'

        if (data := await self.db.find_one(search_dict)):
            return data['translate']

        return


        # if str(locale) == "uk": locale = "ru"   # TODO: make translation for Ukranian
        # if str(locale) not in self.translations.keys(): return
        # if context.location is trans_context.other:
        #     if f"{context.data}.{string.message}" in self.translations[str(locale)].keys(): 
        #         return self.translations[str(locale)][f"{context.data}.{string.message}"]
        #     elif context.data in self.translations[str(locale)].keys():
        #         return self.translations[str(locale)][context.data]
        #     else: return
        # if string.message not in self.translations[str(locale)].keys(): return
        # return self.translations[str(locale)][string.message]


async def setup(bot):
    await bot.tree.set_translator(MeowTranslator())

