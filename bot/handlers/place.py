from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import get_user_subscriptions_with_places

router = Router()


@router.message(Command("myplace"))
async def myplace_handler(message: Message):
    user_id = message.from_user.id

    subscriptions = await get_user_subscriptions_with_places(user_id)

    if not subscriptions:
        await message.answer("У вас нет активных подписок.")
        return

    lines = ["📊 Ваши текущие места:\n"]

    for i, sub in enumerate(subscriptions, start=1):
        place = sub["current_place"] if sub["current_place"] is not None else "нет данных"
        lines.append(
            f"{i}. {sub["competition_name"]}\n"
            f"Место: {place}\n"
        )

    await message.answer("\n".join(lines))