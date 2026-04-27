from __future__ import annotations

from datetime import datetime
from typing import Optional

from database.db import connect_db


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


# =========================================================
# USERS
# =========================================================
async def get_or_create_user(user_id: int):
    async with connect_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()

async def set_user_code(user_id: int, unique_code: int):
    async with connect_db() as db:
        await db.execute("""
            INSERT INTO users (tg_user_id, unique_code)
            VALUES (?, ?)
            ON CONFLICT(tg_user_id)
            DO UPDATE SET unique_code = excluded.unique_code
        """, (user_id, unique_code))
        await db.commit()


async def get_user_code(user_id: int) -> Optional[int]:
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT unique_code
            FROM users
            WHERE tg_user_id = ?
        """, (user_id,))
        row = await cur.fetchone()
        return row["unique_code"] if row else None


# =========================================================
# COMPETITIONS
# =========================================================

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
) -> int:
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


async def update_competition_last_updated(comp_id: int):
    async with connect_db() as db:
        await db.execute("""
            UPDATE competitions
            SET last_updated = ?
            WHERE id = ?
        """, (utc_now(), comp_id))
        await db.commit()


# =========================================================
# APPLICANTS
# =========================================================

async def get_applicants_by_competition(comp_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                id,
                unique_code,
                current_place,
                updated_at,
                competition_id
            FROM applicants
            WHERE competition_id = ?
            ORDER BY unique_code ASC
        """, (comp_id,))
        return await cur.fetchall()


async def get_applicant_by_code_and_comp(code: int, comp_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                id,
                unique_code,
                current_place,
                updated_at,
                competition_id
            FROM applicants
            WHERE unique_code = ?
              AND competition_id = ?
        """, (code, comp_id))
        return await cur.fetchone()


async def insert_applicant(comp_id: int, code: int, place: Optional[int]):
    async with connect_db() as db:
        cur = await db.execute("""
            INSERT INTO applicants (
                competition_id,
                unique_code,
                current_place,
                updated_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            comp_id,
            code,
            place,
            utc_now(),
        ))
        await db.commit()
        return cur.lastrowid


async def update_applicant_place(applicant_id: int, place: Optional[int]):
    async with connect_db() as db:
        await db.execute("""
            UPDATE applicants
            SET current_place = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            place,
            utc_now(),
            applicant_id,
        ))
        await db.commit()


# =========================================================
# SUBSCRIPTIONS
# =========================================================

async def add_subscription(user_id: int, competition_id: int):
    async with connect_db() as db:
        await db.execute(
            """
            INSERT INTO subscriptions (tg_user_id, competition_id, notifications_enabled)
            VALUES (?, ?, 1)
            ON CONFLICT(tg_user_id, competition_id)
            DO UPDATE SET notifications_enabled = 1
            """,
            (user_id, competition_id),
        )
        await db.commit()

async def get_subscribers_by_applicant_id(applicant_id: int) -> list[int]:
    async with connect_db() as db:
        cur = await db.execute(
            """
            SELECT tg_user_id
            FROM subscriptions
            WHERE applicant_id = ?
              AND notifications_enabled = 1
            """,
            (applicant_id,),
        )
        rows = await cur.fetchall()
        return [row["tg_user_id"] for row in rows]


async def get_competition_subscribers(comp_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT tg_user_id
            FROM subscriptions
            WHERE competition_id = ?
              AND notifications_enabled = 1
            ORDER BY tg_user_id ASC
        """, (comp_id,))
        return await cur.fetchall()


async def get_subscribers_by_competition(comp_id: int) -> list[int]:
    async with connect_db() as db:
        cur = await db.execute(
            """
            SELECT tg_user_id
            FROM subscriptions
            WHERE competition_id = ? AND notifications_enabled = 1
            """,
            (comp_id,),
        )
        rows = await cur.fetchall()
        return [row["tg_user_id"] for row in rows]


async def get_user_subscriptions_with_places(user_id: int):
    async with connect_db() as db:
        cur = await db.execute("""
            SELECT
                c.id AS competition_id,
                c.name AS competition_name,
                u.unique_code,
                a.current_place,
                a.updated_at
            FROM subscriptions s
            JOIN competitions c
                ON c.id = s.competition_id
            JOIN users u
                ON u.tg_user_id = s.tg_user_id
            LEFT JOIN applicants a
                ON a.competition_id = c.id
               AND a.unique_code = u.unique_code
            WHERE s.tg_user_id = ?
              AND s.notifications_enabled = 1
            ORDER BY c.name ASC
        """, (user_id,))
        return await cur.fetchall()


async def delete_subscription(user_id: int, competition_id: int):
    async with connect_db() as db:
        await db.execute(
            """
            DELETE FROM subscriptions
            WHERE tg_user_id = ? AND competition_id = ?
            """,
            (user_id, competition_id),
        )
        await db.commit()