from parsers.fetcher import fetch_rating
from database.repository import (
    upsert_applicant,
    update_competition_time,
    get_subscribers_by_code
)

async def update_competition(comp_id: int, qs: str, notify_callback=None):
    rows = await fetch_rating(qs)

    for code, new_place in rows:
        old_place, new_place = await upsert_applicant(code, new_place, comp_id)

        if old_place is not None and old_place != new_place:
            if notify_callback:
                subscribers = await get_subscribers_by_code(code, comp_id)

                await notify_callback(subscribers, code, old_place, new_place)

    await update_competition_time(comp_id)