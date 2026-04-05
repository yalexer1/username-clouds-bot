import asyncpg
import os
from typing import List, Dict, Any
from config import settings

DATABASE_URL = os.getenv("DATABASE_URL")
print("=== DATABASE_URL DEBUG ===")
print(f"Value: {DATABASE_URL}")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set!")
    raise RuntimeError("DATABASE_URL environment variable is missing")
print("==========================")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS found (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            length INTEGER NOT NULL,
            beauty_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shown_to_user BOOLEAN DEFAULT FALSE
        )
    """)
    await conn.close()

async def insert_username(username: str, length: int, beauty_score: int, status: str) -> bool:
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(
            "INSERT INTO found (username, length, beauty_score, status) VALUES ($1, $2, $3, $4)",
            username, length, beauty_score, status
        )
        await conn.close()
        return True
    except Exception as e:
        print(f"Insert error: {e}")
        return False

async def get_free_usernames(length: int, limit: int, offset: int) -> List[Dict[str, Any]]:
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        "SELECT id, username, beauty_score FROM found "
        "WHERE length = $1 AND status = 'free' AND beauty_score >= $2 AND shown_to_user = FALSE "
        "ORDER BY beauty_score DESC, id "
        "LIMIT $3 OFFSET $4",
        length, settings.BEAUTY_SCORE_THRESHOLD, limit, offset
    )
    await conn.close()
    return [{"id": row["id"], "username": row["username"], "beauty_score": row["beauty_score"]} for row in rows]

async def mark_as_shown(ids: List[int]) -> None:
    if not ids:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    for i in ids:
        await conn.execute("UPDATE found SET shown_to_user = TRUE WHERE id = $1", i)
    await conn.close()

async def count_free_usernames(length: int) -> int:
    conn = await asyncpg.connect(DATABASE_URL)
    count = await conn.fetchval(
        "SELECT COUNT(*) FROM found WHERE length = $1 AND status = 'free' AND beauty_score >= $2 AND shown_to_user = FALSE",
        length, settings.BEAUTY_SCORE_THRESHOLD
    )
    await conn.close()
    return count or 0

async def username_exists(username: str) -> bool:
    conn = await asyncpg.connect(DATABASE_URL)
    exists = await conn.fetchval("SELECT 1 FROM found WHERE username = $1", username)
    await conn.close()
    return exists is not None