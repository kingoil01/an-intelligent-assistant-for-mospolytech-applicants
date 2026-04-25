import aiosqlite

DB_PATH = "bot.db"

CREATE_TABLES = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    tg_user_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    select1 TEXT NOT NULL,
    spec_code TEXT NOT NULL,
    edu_form TEXT NOT NULL,
    edu_fin TEXT NOT NULL,
    last_updated DATETIME
);

CREATE TABLE IF NOT EXISTS applicants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_code INTEGER NOT NULL,
    current_place INTEGER,
    updated_at TEXT,
    competition_id INTEGER NOT NULL,
    FOREIGN KEY (competition_id) REFERENCES competitions(id)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER NOT NULL REFERENCES users(tg_user_id),
    applicant_id INTEGER NOT NULL REFERENCES applicants(id),
    notifications_enabled INTEGER NOT NULL DEFAULT 1,
    UNIQUE(tg_user_id, applicant_id)
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()