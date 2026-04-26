import aiosqlite

DB_PATH = "bot.db"

CREATE_TABLES = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    tg_user_id INTEGER PRIMARY KEY,
    unique_code INTEGER
);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    select1 TEXT NOT NULL,
    spec_code TEXT NOT NULL,
    edu_form TEXT NOT NULL,
    edu_fin TEXT NOT NULL,
    last_updated TEXT
);

CREATE TABLE IF NOT EXISTS applicants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    unique_code INTEGER NOT NULL,
    current_place INTEGER,
    updated_at TEXT,
    UNIQUE(competition_id, unique_code),
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    tg_user_id INTEGER NOT NULL,
    competition_id INTEGER NOT NULL,
    notifications_enabled INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (tg_user_id, competition_id),
    FOREIGN KEY (tg_user_id) REFERENCES users(tg_user_id) ON DELETE CASCADE,
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()