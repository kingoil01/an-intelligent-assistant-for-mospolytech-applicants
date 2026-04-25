from database.repository import add_subscription, get_or_create_user


async def subscribe_user_to_applicant(user_id: int, applicant_id: int):
    await get_or_create_user(user_id)
    await add_subscription(user_id, applicant_id)
