from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Я бот для отслеживания конкурсных списков МосПолитеха.\n"
        "Помогу следить за изменением твоего места в рейтинге по выбранным направлениям.\n\n"

        "📌 Доступные команды:\n\n"

        "1️⃣ Сохранить свой уникальный код с госуслуг:\n"
        "/code <ваш_код>\n\n"

        "2️⃣ Отслеживать конкурсную таблицу:\n"
        "/track <ссылка_на_конкурсную_таблицу>\n"
        "Пример:\n"
        "/track https://mospolytech.ru/.../?qs=...\n\n"

        "3️⃣ Посмотреть текущие места по всем подпискам:\n"
        "/myplace\n\n"

        "4️⃣ Перестать отслеживать конкурс:\n"
        "/untrack <ссылка_на_конкурсную_таблицу>\n\n"
    )