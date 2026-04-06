from fastapi import FastAPI
import asyncio
from bot import main as bot_main

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running"}

# Запускаем бота в фоне при старте
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot_main())