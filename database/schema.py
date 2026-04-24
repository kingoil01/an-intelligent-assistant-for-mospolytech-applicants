DB_PATH = "bot.db"

CREATE_TABLES = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    tg_user_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS competitions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT,
    qs            TEXT UNIQUE NOT NULL,
    last_updated  DATETIME
);

CREATE TABLE IF NOT EXISTS applicants (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_code     INTEGER NOT NULL,
    current_place   INTEGER,
    updated_at      DATETIME,
    competition_id  INTEGER NOT NULL,
    UNIQUE(unique_code, competition_id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id            INTEGER NOT NULL,
    applicant_id          INTEGER NOT NULL,
    notifications_enabled INTEGER NOT NULL DEFAULT 1,
    UNIQUE(tg_user_id, applicant_id),
    FOREIGN KEY (tg_user_id) REFERENCES users(tg_user_id) ON DELETE CASCADE,
    FOREIGN KEY (applicant_id) REFERENCES applicants(id) ON DELETE CASCADE
);
"""


async def init_db():
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()