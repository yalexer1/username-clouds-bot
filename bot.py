import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_offsets = {}

async def api_request(length: int, offset: int, limit: int = 10):
    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:10000/get_usernames?length={length}&limit={limit}&offset={offset}"
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Искать username", callback_data="search"),
            InlineKeyboardButton(text="👤 Кто создатель?", callback_data="creator")
        ]
    ])
    await message.answer(
        "Добро пожаловать в Username Clouds☁, мы поможем вам найти красивые NFT через бота",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "creator")
async def show_creator(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await callback.message.edit_text(
        "Мой создатель - t.me/savesep",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await cmd_start(callback.message)
    await callback.answer()

@router.callback_query(lambda c: c.data == "search")
async def ask_length(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5", callback_data="length_5"),
            InlineKeyboardButton(text="6", callback_data="length_6"),
            InlineKeyboardButton(text="7", callback_data="length_7")
        ]
    ])
    await callback.message.edit_text(
        "Выбери длину username для поиска:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("length_"))
async def start_search(callback: CallbackQuery):
    length = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    if user_id not in user_offsets:
        user_offsets[user_id] = {}
    user_offsets[user_id][length] = 0
    await send_usernames(callback.message, length, user_id, offset=0)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("next_"))
async def more_usernames(callback: CallbackQuery):
    _, length_str, offset_str = callback.data.split("_")
    length = int(length_str)
    offset = int(offset_str)
    user_id = callback.from_user.id
    await send_usernames(callback.message, length, user_id, offset)
    await callback.answer()

async def send_usernames(message: types.Message, length: int, user_id: int, offset: int):
    wait_msg = await message.answer(f"🔎 Ищу красивые свободные username из {length} букв... Это может занять несколько секунд")
    usernames = await api_request(length, offset, limit=10)
    await wait_msg.delete()

    if not usernames:
        await message.answer(f"❌ Свободные красивые username для длины {length} закончились. Попробуй другую длину")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="5", callback_data="length_5"),
             InlineKeyboardButton(text="6", callback_data="length_6"),
             InlineKeyboardButton(text="7", callback_data="length_7")]
        ])
        await message.answer("Выбери другую длину:", reply_markup=keyboard)
        return

    response_lines = [f"✅ Нашёл для тебя:"]
    for i, item in enumerate(usernames, 1):
        response_lines.append(f"{i}. @{item['username']} (рейтинг красоты: {item['beauty_score']}/100)")
    text = "\n".join(response_lines)

    new_offset = offset + 10
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Найти ещё", callback_data=f"next_{length}_{new_offset}")]
    ])
    await message.answer(text, reply_markup=keyboard)

    if user_id not in user_offsets:
        user_offsets[user_id] = {}
    user_offsets[user_id][length] = new_offset