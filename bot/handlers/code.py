from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import set_user_code

router = Router()

@router.message(Command("code"))
async def code_handler(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Использование:\n"
            "/code <ваш_unique_code>"
        )
        return

    code_str = args[1].strip()

    if not code_str.isdigit():
        await message.answer("❌ unique_code должен состоять только из цифр.")
        return

    unique_code = int(code_str)

    await set_user_code(message.from_user.id, unique_code)

    await message.answer(
        f"✅ Ваш unique_code сохранён: {unique_code}"
    )