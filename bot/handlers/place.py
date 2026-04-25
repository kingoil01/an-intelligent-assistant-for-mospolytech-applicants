from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import get_user_subscriptions_with_places

router = Router()


@router.message(Command("myplace"))
async def my_place_handler(message: Message):
    user_id = message.from_user.id
    subscriptions = await get_user_subscriptions_with_places(user_id)

    if not subscriptions:
        await message.answer(
            "❌ У вас нет отслеживаемых абитуриентов.\n"
            "Используйте /track <ссылка> <код>."
        )
        return

    lines = ["📊 Ваши места в рейтинге:\n"]

    for sub in subscriptions:
        place = sub["current_place"] if sub["current_place"] is not None else "нет данных"
        updated = sub["updated_at"][:19] if sub["updated_at"] else "никогда"

        lines.append(
            f"🎓 Конкурс: {sub['competition_name']}\n"
            f"Код абитуриента: {sub['unique_code']}\n"
            f"Текущее место: {place}\n"
            f"Обновлено: {updated}\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )

    await message.answer("\n".join(lines))
