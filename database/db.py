from contextlib import asynccontextmanager

import aiosqlite

from config.settings import DATABASE_PATH

DB_PATH = DATABASE_PATH


@asynccontextmanager
async def connect_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db
