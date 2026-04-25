from __future__ import annotations

import logging
from typing import Optional, Sequence

from aiogram import Bot

logger = logging.getLogger(__name__)


async def send_place_change_notification(
    bot: Bot,
    subscribers: Sequence[int],
    code: int,
    old_place: Optional[int],
    new_place: Optional[int],
    competition_name: Optional[str] = None,
):
    if not subscribers:
        return

    header = f"Конкурс: {competition_name}\n" if competition_name else ""

    if new_place is None:
        text = (
            f"🔔 Обновление по коду {code}\n"
            f"{header}"
            f"Код больше не найден в актуальном списке."
        )
    elif old_place is None:
        text = (
            f"🔔 Обновление по коду {code}\n"
            f"{header}"
            f"Текущее место: {new_place}"
        )
    else:
        text = (
            f"🔔 Изменение места по коду {code}\n"
            f"{header}"
            f"Было: {old_place}\n"
            f"Стало: {new_place}"
        )

    for tg_user_id in subscribers:
        try:
            await bot.send_message(tg_user_id, text)
        except Exception:
            logger.exception("Не удалось отправить уведомление пользователю %s", tg_user_id)
