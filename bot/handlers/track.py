from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.track_service import track_competition
from database.repository import get_user_code
from utils.qs import extract_qs

router = Router()

@router.message(Command("track"))
async def track_handler(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Использование:\n"
            "/track <ссылка>\n\n"
            "Пример:\n"
            "/track https://mospolytech.ru/.../?qs=..."
        )
        return

    qs = extract_qs(args[1].strip())

    if not qs:
        await message.answer("❌ Не удалось извлечь qs из ссылки.")
        return

    unique_code = await get_user_code(message.from_user.id)

    if not unique_code:
        await message.answer(
            "❌ Сначала задайте свой unique_code:\n"
            "/code 1234567"
        )
        return

    await message.answer("⏳ Подключаю конкурс...")

    try:
        applicant, competition = await track_competition(
            user_id=message.from_user.id,
            qs=qs,
            unique_code=unique_code,
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        return

    if applicant is None:
        await message.answer(
            f"❌ Ваш код {unique_code} не найден в этом конкурсе."
        )
        return

    await message.answer(
        "✅ Подписка оформлена!\n\n"
        f"Конкурс: {competition['name']}\n"
        f"Ваш код: {unique_code}\n"
        f"Текущее место: {applicant['current_place']}"
    )