from bot import db


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
