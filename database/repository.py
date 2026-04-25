from __future__ import annotations

from datetime import datetime
from typing import Optional

from database.db import connect_db


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


async def get_competition_by_qs(qs: str):
    async with connect_db() as db:
        cur = await db.execute(
            "SELECT id, name, qs, last_updated FROM competitions WHERE qs = ?",
            (qs,),
        )
        return await cur.fetchone()


async def get_competition_by_id(comp_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                id,
                name,
                select1,
                spec_code,
                edu_form,
                edu_fin,
                last_updated
            FROM competitions
            WHERE id = ?
        """, (comp_id,))
        return await cur.fetchone()


async def get_or_create_competition(qs: str, name: str = "Конкурс"):
    competition = await get_competition_by_qs(qs)
    if competition:
        return competition

    async with connect_db() as db:
        await db.execute(
            "INSERT INTO competitions (name, qs, last_updated) VALUES (?, ?, NULL)",
            (name, qs),
        )
        await db.commit()

    return await get_competition_by_qs(qs)


async def get_all_competitions():
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                id,
                name,
                select1,
                spec_code,
                edu_form,
                edu_fin,
                last_updated
            FROM competitions
            ORDER BY id ASC
        """)
        return await cur.fetchall()


async def competition_has_applicants(comp_id: int) -> bool:
    async with connect_db() as db:
        cur = await db.execute(
            "SELECT 1 FROM applicants WHERE competition_id = ? LIMIT 1",
            (comp_id,),
        )
        return (await cur.fetchone()) is not None


async def update_competition_last_updated(comp_id: int):
    async with connect_db() as db:
        await db.execute(
            "UPDATE competitions SET last_updated = ? WHERE id = ?",
            (utc_now(), comp_id),
        )
        await db.commit()


async def get_applicants_by_competition(comp_id: int):
    async with connect_db() as db:
        cur = await db.execute(
            """
            SELECT id, unique_code, current_place, updated_at, competition_id
            FROM applicants
            WHERE competition_id = ?
            ORDER BY unique_code ASC
            """,
            (comp_id,),
        )
        return await cur.fetchall()


async def get_applicant_by_code_and_comp(code: int, comp_id: int):
    async with connect_db() as db:
        cur = await db.execute(
            """
            SELECT id, unique_code, current_place, updated_at, competition_id
            FROM applicants
            WHERE unique_code = ? AND competition_id = ?
            """,
            (code, comp_id),
        )
        return await cur.fetchone()


async def insert_applicant(comp_id: int, code: int, place: Optional[int]):
    async with connect_db() as db:
        cur = await db.execute(
            """
            INSERT INTO applicants (unique_code, current_place, updated_at, competition_id)
            VALUES (?, ?, ?, ?)
            """,
            (code, place, utc_now(), comp_id),
        )
        await db.commit()
        return cur.lastrowid


async def update_applicant_place(applicant_id: int, place: Optional[int]):
    async with connect_db() as db:
        await db.execute(
            """
            UPDATE applicants
            SET current_place = ?, updated_at = ?
            WHERE id = ?
            """,
            (place, utc_now(), applicant_id),
        )
        await db.commit()


async def get_subscribers_by_applicant_id(applicant_id: int) -> list[int]:
    async with connect_db() as db:
        cur = await db.execute(
            """
            SELECT tg_user_id
            FROM subscriptions
            WHERE applicant_id = ? AND notifications_enabled = 1
            ORDER BY tg_user_id ASC
            """,
            (applicant_id,),
        )
        rows = await cur.fetchall()
        return [row["tg_user_id"] for row in rows]


async def get_or_create_user(user_id: int):
    async with connect_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()


async def add_subscription(user_id: int, applicant_id: int):
    async with connect_db() as db:
        await db.execute(
            """
            INSERT INTO subscriptions (tg_user_id, applicant_id, notifications_enabled)
            VALUES (?, ?, 1)
            ON CONFLICT(tg_user_id, applicant_id)
            DO UPDATE SET notifications_enabled = 1
            """,
            (user_id, applicant_id),
        )
        await db.commit()


async def get_user_subscriptions_with_places(user_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                a.unique_code,
                a.current_place,
                a.updated_at,
                c.name AS competition_name,
                s.notifications_enabled
            FROM subscriptions s
            JOIN applicants a ON a.id = s.applicant_id
            JOIN competitions c ON c.id = a.competition_id
            WHERE s.tg_user_id = ? AND s.notifications_enabled = 1
            ORDER BY c.name ASC, a.unique_code ASC
        """, (user_id,))
        return await cur.fetchall()


async def find_competition(
    select1: str,
    spec_code: str,
    edu_form: str,
    edu_fin: str,
):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                id,
                name,
                select1,
                spec_code,
                edu_form,
                edu_fin,
                last_updated
            FROM competitions
            WHERE select1 = ?
              AND spec_code = ?
              AND edu_form = ?
              AND edu_fin = ?
        """, (
            select1,
            spec_code,
            edu_form,
            edu_fin,
        ))
        return await cur.fetchone()


async def create_competition(
    name: str,
    select1: str,
    spec_code: str,
    edu_form: str,
    edu_fin: str,
):
    async with connect_db() as db:
        cur = await db.execute("""
            INSERT INTO competitions (
                name,
                select1,
                spec_code,
                edu_form,
                edu_fin,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, NULL)
        """, (
            name,
            select1,
            spec_code,
            edu_form,
            edu_fin,
        ))
        await db.commit()
        return cur.lastrowid
