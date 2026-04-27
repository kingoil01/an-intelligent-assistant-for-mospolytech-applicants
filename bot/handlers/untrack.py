from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.repository import get_user_subscriptions_with_places, delete_subscription

router = Router()


class UntrackState(StatesGroup):
    waiting_for_number = State()


@router.message(Command("untrack"))
async def untrack_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    subscriptions = await get_user_subscriptions_with_places(user_id)

    if not subscriptions:
        await message.answer("У вас нет активных подписок.")
        return

    text = ["Введите номер подписки для удаления:\n"]

    for i, sub in enumerate(subscriptions, start=1):
        text.append(f"{i}. {sub["competition_name"]}")

    await state.update_data(subscriptions=[dict(sub) for sub in subscriptions])
    await state.set_state(UntrackState.waiting_for_number)

    await message.answer("\n".join(text))


@router.message(UntrackState.waiting_for_number)
async def untrack_finish(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите корректный номер.")
        return

    index = int(message.text)

    data = await state.get_data()
    subscriptions = data["subscriptions"]

    if index < 1 or index > len(subscriptions):
        await message.answer("Нет подписки с таким номером.")
        return

    selected = subscriptions[index - 1]

    await delete_subscription(
        user_id=message.from_user.id,
        competition_id=selected["competition_id"]
    )

    await message.answer(f"Подписка удалена:\n{selected['competition_name']}")
    await state.clear()