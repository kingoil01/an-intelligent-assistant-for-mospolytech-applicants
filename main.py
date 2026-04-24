import asyncio
import logging
from aiogram import Bot, Dispatcher
from database.schema import init_db

from config.config import BOT_TOKEN
from bot.handlers.start import router as start_router
from bot.handlers.track import router as track_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s/%(levelname)s/%(name)s - %(message)s"
    )

    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(track_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())