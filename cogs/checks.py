from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['Koteika']
collection = db.members


def is_secret(ctx):
    try: id_ = ctx.author.id
    except: id_ = ctx.id
    info = collection.find_one({"id": id_})["access_level"]
    return 'secret' == info


def is_white(ctx):
    try:
        id_ = ctx.author.id
    except:
        id_ = ctx.id
    info = collection.find_one({"id": id_})["access_level"]
    return info in ('white', 'secret')


def is_not_black(ctx):
    try:
        id_ = ctx.author.id
    except:
        id_ = ctx.id
    info = collection.find_one({"id": id_})["access_level"]
    return "black" != info