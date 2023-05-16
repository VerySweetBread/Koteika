from bot import db
from schedule import every, clear, run_pending
import asyncio
from datetime import datetime, timedelta
from loguru import logger

daysoftheweek = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

async def save_activity():
    day = (datetime.now()-timedelta(1)).weekday()
    async for data in db.history.find({"type": "server"}):
        await db.history.update_one(
            {"type": "server", "id": data['id']},
            {
                "$push": 
                    {f"avarage.{i}": data['current'][str(i)] for i in range(24)},
                "$set":
                    {f'yesterday.{i}': data['current'][str(i)] for i in range(24)}
            }
        )
        await db.history.update_one(
            {"type": "server", "id": data['id']},
            {
                "$push": 
                    {f"history.{daysoftheweek[day]}.{i}": data['current'][str(i)] for i in range(24)}, 
                "$set":
                    {f"current.{i}": 0 for i in range(24)}
            }
        )

async def db_sync_hour():
    logger.info("Регистрация за час")
    async for member in db.members.find():
        await db.members.update_one({"_id": member["_id"]}, {"$set": {f"history.hour.{int(datetime.now().timestamp())}": member["exp"]}})
        if 'guild_stat' in member.keys():
            for guild in member["guild_stat"].keys():
                await db.members.update_one({"_id": member["_id"]}, {"$set": {f"guild_stat.{guild}.history.hour.{int(datetime.now().timestamp())}": member["guild_stat"][guild]["exp"]}})
    logger.info("Регистрация завершена")


async def db_sync_day():
    logger.info("Регистрация за день")
    async for member in db.members.find():
        await db.members.update_one({"_id": member["_id"]}, {"$set": {f"history.day.{int(datetime.now().timestamp())}": member["exp"]}})
        for guild in member["guild_stat"].keys():
            await db.members.update_one({"_id": member["_id"]}, {"$set": {f"guild_stat.{guild}.history.day.{int(datetime.now().timestamp())}": member["guild_stat"][guild]["exp"]}})
    logger.info("Регистрация завершена")
#            await self.bot.get_user(self.bot.owner_id).send("Завершено за день????")


async def main(bot):
    clear()

    every().day.at('00:00:00').do(lambda: asyncio.run_coroutine_threadsafe(save_activity(), bot.loop))
    every().hours.at("00:00").do(lambda: asyncio.run_coroutine_threadsafe(db_sync_hour(), bot.loop))
    every().day.at("00:00:00").do(lambda: asyncio.run_coroutine_threadsafe(db_sync_day(), bot.loop))

    while True:
        run_pending()
        await asyncio.sleep(1)

async def setup(bot):
    asyncio.create_task(main(bot))
