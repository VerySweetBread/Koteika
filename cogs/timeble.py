from bot import db
from schedule import every, clear, run_pending
import asyncio
from datetime import datetime, timedelta
from loguru import logger

daysoftheweek = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

def save_activity():
    day = (datetime.now()-timedelta(1)).weekday()
    for data in db.history.find({"type": "server"}):
        db.history.update_one(
            {"type": "server", "id": data['id']},
            {
                "$push": 
                    {f"avarage.{i}": data['current'][str(i)] for i in range(24)},
                "$set":
                    {f'yesterday.{i}': data['current'][str(i)] for i in range(24)}
            }
        )
        db.history.update_one(
            {"type": "server", "id": data['id']},
            {
                "$push": 
                    {f"history.{daysoftheweek[day]}.{i}": data['current'][str(i)] for i in range(24)}, 
                "$set":
                    {f"current.{i}": 0 for i in range(24)}
            }
        )

def db_sync_hour():
    logger.info("Регистрация за час")
    for member in list(db.members.find()):
        db.members.update_one({"_id": member["_id"]}, {"$set": {f"history.hour.{int(datetime.now().timestamp())}": member["exp"]}})
        if 'guild_stat' in member.keys():
            for guild in member["guild_stat"].keys():
                db.members.update_one({"_id": member["_id"]}, {"$set": {f"guild_stat.{guild}.history.hour.{int(datetime.now().timestamp())}": member["guild_stat"][guild]["exp"]}})
    logger.info("Регистрация завершена")


def db_sync_day():
    logger.info("Регистрация за день")
    for member in list(db.members.find()):
        db.members.update_one({"_id": member["_id"]}, {"$set": {f"history.day.{int(datetime.now().timestamp())}": member["exp"]}})
        for guild in member["guild_stat"].keys():
            db.members.update_one({"_id": member["_id"]}, {"$set": {f"guild_stat.{guild}.history.day.{int(datetime.now().timestamp())}": member["guild_stat"][guild]["exp"]}})
    logger.info("Регистрация завершена")
#            await self.bot.get_user(self.bot.owner_id).send("Завершено за день????")


async def main():
    clear()

    every().day.at('00:00:00').do(save_activity)
    every().hours.at("00:00").do(db_sync_hour)
    every().day.at("00:00:00").do(db_sync_day)

    while True:
        run_pending()
        await asyncio.sleep(1)

async def setup(_):
    asyncio.create_task(main())
