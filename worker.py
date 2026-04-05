import asyncio
import logging
from database import insert_username, username_exists
from generator import generate_usernames_for_length
from filters import calculate_beauty_score
from checker import checker
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_username(username: str, length: int):
    if await username_exists(username):
        return
    status = await checker.check(username)
    if status != "free":
        return
    score = calculate_beauty_score(username)
    if score >= settings.BEAUTY_SCORE_THRESHOLD:
        await insert_username(username, length, score, "free")
        logger.info(f"Found free username: @{username} (score={score})")

async def scan_worker():
    await checker.start()
    logger.info("Worker started")
    try:
        while True:
            for length in (5, 6, 7):
                usernames = generate_usernames_for_length(length, count=20)
                for username in usernames:
                    await process_username(username, length)
                    await asyncio.sleep(settings.MT_PROTO_DELAY)
            logger.info("Worker cycle completed, sleeping...")
            await asyncio.sleep(settings.WORKER_SLEEP)
    except asyncio.CancelledError:
        logger.info("Worker cancelled")
    finally:
        await checker.stop()