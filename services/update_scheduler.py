from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.notifications import send_place_change_notification
from database.repository import get_all_competitions
from pipeline.update_pipeline import update_competition

logger = logging.getLogger(__name__)


def build_notify_callback(bot: Bot):
    async def _notify(subscribers, code, old_place, new_place, competition_name=None):
        await send_place_change_notification(
            bot=bot,
            subscribers=subscribers,
            code=code,
            old_place=old_place,
            new_place=new_place,
            competition_name=competition_name,
        )

    return _notify


async def update_all_competitions(bot: Bot):
    competitions = await get_all_competitions()

    if not competitions:
        logger.info("Нет конкурсов для обновления")
        return

    logger.info("Начинаю обновление %d конкурсов", len(competitions))
    notify_callback = build_notify_callback(bot)

    for comp in competitions:
        try:
            stats = await update_competition(comp_id=comp["id"], notify_callback=notify_callback)
            logger.info(
                "Конкурс %s обновлён: fetched=%s inserted=%s updated=%s removed=%s",
                comp["id"],
                stats["fetched"],
                stats["inserted"],
                stats["updated"],
                stats["removed"],
            )
        except Exception:
            logger.exception("Ошибка при обновлении конкурса %s", comp["id"])


async def start_scheduler(bot: Bot, interval_minutes: int = 5):
    while True:
        try:
            await update_all_competitions(bot)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Ошибка в планировщике обновления")
        await asyncio.sleep(interval_minutes * 60)
