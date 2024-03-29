from bot import db
from discord.app_commands   import TranslationContextLocation as trans_loc
from discord import app_commands

def region_to_str(region):
    # if region == discord.VoiceRegion.russia:
    #     return "RU"
    # elif region == discord.VoiceRegion.japan:
    #     return "JP"
    # else:
    return "RU"


def translate(string, region):
    if string is not None:
        if string.startswith("$"):
            string = string.replace("$", "")
            string = string.split("_")

            print(region)

            pack = db.strings.find_one({"lang": region})
            print(pack)

            for i in string:
                pack = pack[i]
                print(pack)

            return pack
        else:
            return string

async def get_text(inter, string, location = None):
    data = await inter.translate(
        string=app_commands.locale_str(string),
        locale=inter.locale,
        data=location
    )

    return data or string

