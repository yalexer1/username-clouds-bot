import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, UsernameNotOccupiedError
from config import settings

class UsernameChecker:
    def __init__(self):
        self.client = None

    async def start(self):
        self.client = TelegramClient(
            StringSession(settings.SESSION_STRING),
            settings.API_ID,
            settings.API_HASH
        )
        await self.client.start()
        print("Telethon client started")

    async def stop(self):
        if self.client:
            await self.client.disconnect()

    async def check_mtproto(self, username: str) -> bool:
        if not self.client:
            raise RuntimeError("Telethon client not started")
        try:
            await self.client.get_entity(username)
            return False
        except UsernameNotOccupiedError:
            return True
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            return await self.check_mtproto(username)
        except Exception:
            return False

    async def check_fragment(self, username: str) -> str:
        url = f"{settings.FRAGMENT_BASE_URL}/{username}"
        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                try:
                    async with session.get(url, timeout=10) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        if soup.find(text=re.compile(r"Place a bid", re.I)):
                            return "auction"
                        else:
                            return "free"
                except Exception:
                    if attempt == 2:
                        return "error"
                    await asyncio.sleep(2 ** attempt)
        return "error"

    async def check(self, username: str) -> str:
        # Временно отключаем Fragment, чтобы быстрее наполнить базу
        is_free = await self.check_mtproto(username)
        return "free" if is_free else "taken"

checker = UsernameChecker()