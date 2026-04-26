from database.repository import (
    get_user_code,
    find_competition,
    create_competition,
    get_competition_by_id,
    get_or_create_user,
    add_subscription,
    get_applicant_by_code_and_comp,
)
from utils.qs import extract_qs
from utils.qs_decoder import decode_qs
from pipeline.update_pipeline import update_competition


async def track_competition(user_id: int, url: str):
    unique_code = await get_user_code(user_id)

    if not unique_code:
        raise ValueError("Сначала укажите код через /code")

    qs = extract_qs(url)
    params = decode_qs(qs)

    competition = await find_competition(
        params["select1"],
        params["spec_code"],
        params["edu_form"],
        params["edu_fin"],
    )

    is_new = False

    if not competition:
        comp_id = await create_competition(
            name=f"{params['spec_code']} | {params['edu_form']} | {params['edu_fin']}",
            select1=params["select1"],
            spec_code=params["spec_code"],
            edu_form=params["edu_form"],
            edu_fin=params["edu_fin"],
        )
        competition = await get_competition_by_id(comp_id)
        is_new = True
    else:
        comp_id = competition["id"]

    if is_new:
        await update_competition(comp_id)

    applicant = await get_applicant_by_code_and_comp(unique_code, comp_id)

    if not applicant:
        return None, competition

    await get_or_create_user(user_id)
    await add_subscription(user_id, competition["id"])

    return applicant["current_place"], competition