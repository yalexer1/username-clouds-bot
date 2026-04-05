import aiosqlite
import tempfile
import os
from typing import List, Dict, Any
from config import settings

# Формируем путь к БД в /tmp (или в рабочей директории, если не на Render)
if os.environ.get('RENDER'):
    DB_PATH = os.path.join('/tmp', 'usernames.db')
else:
    DB_PATH = 'usernames.db'

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS found (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                length INTEGER NOT NULL,
                beauty_score INTEGER NOT NULL,
                status TEXT NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                shown_to_user BOOLEAN DEFAULT 0
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_length_status_score ON found(length, status, beauty_score, shown_to_user)")
        await db.commit()

async def insert_username(username: str, length: int, beauty_score: int, status: str) -> bool:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO found (username, length, beauty_score, status) VALUES (?, ?, ?, ?)",
                (username, length, beauty_score, status)
            )
            await db.commit()
            return True
    except aiosqlite.IntegrityError:
        return False

async def get_free_usernames(length: int, limit: int, offset: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, username, beauty_score FROM found "
            "WHERE length = ? AND status = 'free' AND beauty_score >= ? AND shown_to_user = 0 "
            "ORDER BY beauty_score DESC, id "
            "LIMIT ? OFFSET ?",
            (length, settings.BEAUTY_SCORE_THRESHOLD, limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": row["id"], "username": row["username"], "beauty_score": row["beauty_score"]} for row in rows]

async def mark_as_shown(ids: List[int]) -> None:
    if not ids:
        return
    placeholders = ",".join("?" * len(ids))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE found SET shown_to_user = 1 WHERE id IN ({placeholders})",
            ids
        )
        await db.commit()

async def count_free_usernames(length: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM found WHERE length = ? AND status = 'free' AND beauty_score >= ? AND shown_to_user = 0",
            (length, settings.BEAUTY_SCORE_THRESHOLD)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def username_exists(username: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM found WHERE username = ?", (username,)) as cursor:
            row = await cursor.fetchone()
            return row is not None