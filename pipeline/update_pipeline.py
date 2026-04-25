from __future__ import annotations

from typing import Awaitable, Callable, Optional

from database.repository import (
    get_applicants_by_competition,
    get_competition_by_id,
    get_subscribers_by_applicant_id,
    insert_applicant,
    update_applicant_place,
    update_competition_last_updated,
)
from parsers.fetcher import fetch_rating

NotifyCallback = Callable[
    [list[int], int, Optional[int], Optional[int], Optional[str]],
    Awaitable[None],
]


async def update_competition(
    comp_id: int,
    notify_callback: NotifyCallback | None = None,
):
    competition = await get_competition_by_id(comp_id)
    competition_name = competition["name"] if competition else None

    rows = await fetch_rating(
        competition["select1"],
        competition["spec_code"],
        competition["edu_form"],
        competition["edu_fin"],
    )

    fetched_map: dict[int, int] = {code: place for code, place in rows}

    existing_rows = await get_applicants_by_competition(comp_id)
    existing_by_code = {row["unique_code"]: row for row in existing_rows}
    seen_codes: set[int] = set()

    inserted = 0
    updated = 0
    removed = 0

    for code, new_place in fetched_map.items():
        seen_codes.add(code)
        existing = existing_by_code.get(code)

        if existing is None:
            await insert_applicant(comp_id, code, new_place)
            inserted += 1
            continue

        old_place = existing["current_place"]
        if old_place != new_place:
            await update_applicant_place(existing["id"], new_place)
            updated += 1

            if (
                notify_callback is not None
                and old_place is not None
                and old_place != new_place
            ):
                subscribers = await get_subscribers_by_applicant_id(existing["id"])
                if subscribers:
                    await notify_callback(
                        subscribers,
                        code,
                        old_place,
                        new_place,
                        competition_name,
                    )

    for code, existing in existing_by_code.items():
        if code in seen_codes:
            continue

        old_place = existing["current_place"]
        if old_place is None:
            continue

        await update_applicant_place(existing["id"], None)
        removed += 1

        if notify_callback is not None:
            subscribers = await get_subscribers_by_applicant_id(existing["id"])
            if subscribers:
                await notify_callback(
                    subscribers,
                    code,
                    old_place,
                    None,
                    competition_name,
                )

    await update_competition_last_updated(comp_id)

    return {
        "fetched": len(fetched_map),
        "inserted": inserted,
        "updated": updated,
        "removed": removed,
    }
