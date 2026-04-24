from pipeline.pipeline import update_competition
from database.repository import get_or_create_competition


async def track_competition(qs: str):
    comp_id = await get_or_create_competition(qs)

    # первичное обновление
    await update_competition(comp_id, qs)

    return comp_id