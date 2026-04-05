import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict, Any
import uvicorn

from database import init_db, get_free_usernames, mark_as_shown, count_free_usernames
from worker import scan_worker
from bot import dp, bot
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    worker_task = asyncio.create_task(scan_worker())
    bot_task = asyncio.create_task(dp.start_polling(bot))
    yield
    worker_task.cancel()
    bot_task.cancel()
    await asyncio.gather(worker_task, bot_task, return_exceptions=True)
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/get_usernames")
async def get_usernames(
    length: int = Query(..., ge=5, le=7),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    total = await count_free_usernames(length)
    if offset >= total:
        return []
    usernames = await get_free_usernames(length, limit, offset)
    ids = [u["id"] for u in usernames]
    await mark_as_shown(ids)
    return [{"username": u["username"], "beauty_score": u["beauty_score"]} for u in usernames]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=False)