from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.track_service import track_competition
from utils.qs import extract_qs

router = Router()


@router.message(Command("track"))
async def track_handler(message: Message):
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.answer(
            "Использование: /track <ссылка> <unique_code>\n"
            "Пример:\n"
            "/track https://mospolytech.ru/.../?qs=... 1234567"
        )
        return

    url = args[1].strip()
    code_str = args[2].strip()

    if not code_str.isdigit():
        await message.answer("❌ unique_code должен состоять только из цифр.")
        return

    unique_code = int(code_str)
    qs = extract_qs(url)

    if not qs:
        await message.answer("❌ Не удалось найти qs в ссылке.")
        return

    await message.answer("⏳ Обрабатываю конкурс...")

    try:
        applicant, competition = await track_competition(
            user_id=message.from_user.id,
            qs=qs,
            unique_code=unique_code,
        )
    except Exception as e:
        await message.answer(f"❌ Не удалось обработать конкурс: {e}")
        return

    if applicant is None:
        await message.answer(
            f"❌ Код {unique_code} не найден в данном списке."
        )
        return

    current_place = applicant["current_place"]
    current_place_text = str(current_place) if current_place is not None else "нет данных"

    await message.answer(
        "✅ Подписка оформлена!\n\n"
        f"Конкурс: {competition['name']}\n"
        f"Код: {unique_code}\n"
        f"Текущее место: {current_place_text}"
    )
