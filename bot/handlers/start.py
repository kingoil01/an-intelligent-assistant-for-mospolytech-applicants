from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Я могу отслеживать конкурсные списки.\n"
        "Команда:\n"
        "/track <ссылка_на_qs> <unique_code>\n\n"
        "Проверка подписок:\n"
        "/myplace"
    )
