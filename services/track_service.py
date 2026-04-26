from database.repository import (
    find_competition,
    create_competition,
    get_competition_by_id,
    get_applicant_by_code_and_comp,
    get_or_create_user,
    add_subscription,
)
from pipeline.update_pipeline import update_competition
from utils.qs_decoder import decode_qs


async def track_competition(user_id: int, qs: str, unique_code: int):
    params = decode_qs(qs)
    print("DECODED PARAMS:", params)

    competition = await find_competition(
        params["select1"],
        params["spec_code"],
        params["edu_form"],
        params["edu_fin"],
    )

    is_new_competition = False

    if competition:
        comp_id = competition["id"]
    else:
        comp_id = await create_competition(
            name=f"{params['spec_code']} | {params['edu_form']} | {params['edu_fin']}",
            select1=params["select1"],
            spec_code=params["spec_code"],
            edu_form=params["edu_form"],
            edu_fin=params["edu_fin"],
        )

        competition = await get_competition_by_id(comp_id)
        is_new_competition = True

    # обновляем таблицу конкурса
    if is_new_competition:
        await update_competition(comp_id)

    # ищем абитуриента
    applicant = await get_applicant_by_code_and_comp(unique_code, comp_id)

    if applicant is None:
        return None, competition

    # создаём пользователя и подписку
    await get_or_create_user(user_id)
    await add_subscription(user_id, applicant["id"])

    return applicant, competition