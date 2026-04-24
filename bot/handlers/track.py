from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.qs import extract_qs

router = Router()


@router.message(Command("track"))
async def track_handler(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование: /track <ссылка>")
        return

    url = args[1]
    qs = extract_qs(url)

    if not qs:
        await message.answer("Не удалось найти qs в ссылке 😕")
        return

    await message.answer("⏳ Обрабатываю конкурс...")
    await message.answer(f"✅ Конкурс добавлен!\nID:")