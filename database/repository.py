import aiosqlite
from datetime import datetime

from database.db import DB_PATH

async def get_competitions():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM competitions")
        return await cur.fetchall()


async def update_competition_time(comp_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE competitions SET last_updated=? WHERE id=?",
            (datetime.utcnow().isoformat(), comp_id)
        )
        await db.commit()

async def get_applicant(db, code: int, comp_id: int):
    cur = await db.execute(
        "SELECT * FROM applicants WHERE unique_code=? AND competition_id=?",
        (code, comp_id)
    )
    return await cur.fetchone()


async def upsert_applicant(code: int, place: int, comp_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT current_place FROM applicants WHERE unique_code=? AND competition_id=?",
            (code, comp_id)
        )
        row = await cur.fetchone()

        old_place = row["current_place"] if row else None

        if row:
            await db.execute(
                """
                UPDATE applicants
                SET current_place=?, updated_at=?
                WHERE unique_code=? AND competition_id=?
                """,
                (place, datetime.utcnow().isoformat(), code, comp_id)
            )
        else:
            await db.execute(
                """
                INSERT INTO applicants (unique_code, current_place, competition_id, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (code, place, comp_id, datetime.utcnow().isoformat())
            )

        await db.commit()

        return old_place, place

async def get_subscribers(applicant_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT tg_user_id
            FROM subscriptions
            WHERE applicant_id=? AND notifications_enabled=1
            """,
            (applicant_id,)
        )
        return await cur.fetchall()

async def get_subscribers_by_code(code: int, comp_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
            SELECT s.tg_user_id
            FROM subscriptions s
            JOIN applicants a ON a.id = s.applicant_id
            WHERE a.unique_code=? AND a.competition_id=?
        """, (code, comp_id))

        return await cur.fetchall()

async def get_or_create_competition(qs: str, name: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT * FROM competitions WHERE qs=?",
            (qs,)
        )
        comp = await cur.fetchone()

        if comp:
            return comp["id"]

        cur = await db.execute(
            "INSERT INTO competitions (qs, name) VALUES (?, ?)",
            (qs, name or "Unnamed")
        )

        await db.commit()
        return cur.lastrowid