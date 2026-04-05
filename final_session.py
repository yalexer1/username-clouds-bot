import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 37779119
API_HASH = "77062d4eaad215d7664fe96300df6ed2"

async def main():
    # Используем StringSession для генерации строки
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    session_string = client.session.save()
    print("\n" + "="*60)
    print("ВАША SESSION_STRING (скопируйте полностью):")
    print("="*60)
    print(session_string)
    print("="*60)
    await client.disconnect()

asyncio.run(main())