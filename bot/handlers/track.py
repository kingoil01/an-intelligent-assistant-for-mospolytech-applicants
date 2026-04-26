from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.track_service import track_competition

router = Router()


@router.message(Command("track"))
async def track_handler(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        await message.answer("Использование: /track <ссылка>")
        return

    url = args[1]

    try:
        place, competition = await track_competition(
            user_id=message.from_user.id,
            url=url
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        return

    if place is None:
        await message.answer("❌ Ваш код не найден в этом конкурсе")
        return

    await message.answer(
        f"✅ Подписка оформлена!\n\n"
        f"Конкурс: {competition['name']}\n"
        f"Текущее место: {place}"
    )