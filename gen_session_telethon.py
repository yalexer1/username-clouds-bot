import asyncio
from telethon import TelegramClient

API_ID = 37779119
API_HASH = "77062d4eaad215d7664fe96300df6ed2"

async def main():
    # Создаём клиент с временной сессией
    client = TelegramClient("temp_session", API_ID, API_HASH)
    await client.start()
    # Экспортируем строку сессии
    session_string = await client.export_session_string()
    print("\n" + "="*60)
    print("ВАША СТРОКА СЕССИИ (скопируйте её полностью):")
    print("="*60)
    print(session_string)
    print("="*60)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())