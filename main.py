import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher

from bot.handlers.place import router as place_router
from bot.handlers.start import router as start_router
from bot.handlers.track import router as track_router
from bot.handlers.code import router as code_router
from config.settings import BOT_TOKEN, UPDATE_INTERVAL_MINUTES
from database.schema import init_db
from services.update_scheduler import start_scheduler


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(track_router)
    dp.include_router(place_router)
    dp.include_router(code_router)

    scheduler_task = asyncio.create_task(
        start_scheduler(bot=bot, interval_minutes=UPDATE_INTERVAL_MINUTES)
    )

    try:
        await dp.start_polling(bot)
    finally:
        scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
