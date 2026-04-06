import asyncio
import random
import string
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, UsernameNotOccupiedError
from config import settings

# --- Инициализация бота ---
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Хранилище показанных username в оперативной памяти ---
# Структура: {user_id: {length: set('shown_usernames')}}
user_shown = {}

# --- Telethon клиент (один на весь бот) ---
_client = None

async def get_client():
    global _client
    if _client is None:
        _client = TelegramClient(StringSession(settings.SESSION_STRING), settings.API_ID, settings.API_HASH)
        await _client.start()
        print("Telethon client started")
    return _client

async def is_username_free(username: str) -> bool:
    """Проверяет, свободен ли username через MTProto API."""
    client = await get_client()
    try:
        await client.get_entity(username)
        return False
    except UsernameNotOccupiedError:
        return True
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await is_username_free(username)
    except Exception:
        return False

def generate_pretty_usernames(length: int, count: int = 30) -> list:
    """Генерирует красивые username (без проверки)."""
    generated = set()
    # Базовые красивые слова
    bases = [
        "star", "moon", "sun", "sky", "cloud", "dream", "heart", "flame", "glory", "magic",
        "noble", "ocean", "peace", "queen", "rainy", "smart", "trust", "unity", "vivid", "young",
        "zebra", "apple", "brain", "eagle", "ideal", "jolly", "karma", "light", "angel", "bliss"
    ]
    suffixes = ["er", "ly", "ing", "y", "ic", "al", "ous", "ive", "ful", "ish"]
    consonants = list("bcdfghjklmnpqrstvwxyz")
    vowels = list("aeiou")

    # 1. Слова подходящей длины
    candidates = [w for w in bases if len(w) == length]
    # 2. Слова + суффиксы
    for w in bases:
        if len(w) <= length - 2:
            suf = random.choice(suffixes)
            cand = (w + suf)[:length]
            if len(cand) == length:
                candidates.append(cand)
    # 3. Leet-варианты
    for w in bases:
        if len(w) == length:
            leet = w.replace('a','4').replace('e','3').replace('i','1').replace('o','0').replace('s','5')
            if leet != w:
                candidates.append(leet)
    # 4. CVCVC слоги
    for _ in range(count):
        cand = ''.join(random.choice(consonants) if i%2==0 else random.choice(vowels) for i in range(length))
        candidates.append(cand)
    # 5. Случайные буквы
    for _ in range(count):
        candidates.append(''.join(random.choices(string.ascii_lowercase, k=length)))
    # Уникализация
    random.shuffle(candidates)
    for cand in candidates:
        if cand not in generated and len(cand) == length and cand.islower() and cand.isalpha():
            generated.add(cand)
            if len(generated) >= count:
                break
    while len(generated) < count:
        generated.add(''.join(random.choices(string.ascii_lowercase, k=length)))
    return list(generated)

# --- Хэндлеры ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Искать username", callback_data="search"),
            InlineKeyboardButton(text="👤 Кто создатель?", callback_data="creator")
        ]
    ])
    await message.answer(
        "Добро пожаловать в Username Clouds☁, тут вы можете найти username на свой вкус и цвет!",
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
    # Инициализируем хранилище для пользователя, если его нет
    if user_id not in user_shown:
        user_shown[user_id] = {}
    if length not in user_shown[user_id]:
        user_shown[user_id][length] = set()
    await send_usernames(callback.message, length, user_id)

@router.callback_query(lambda c: c.data.startswith("next_"))
async def more_usernames(callback: CallbackQuery):
    _, length_str = callback.data.split("_")
    length = int(length_str)
    user_id = callback.from_user.id
    await send_usernames(callback.message, length, user_id)

async def send_usernames(message: types.Message, length: int, user_id: int):
    wait_msg = await message.answer(f"🔎 Ищу красивые свободные username из {length} букв... Это может занять несколько секунд")
    
    shown_set = user_shown[user_id][length]
    found = []
    attempts = 0
    # Пока не нашли 10 свободных и не превысили лимит попыток
    while len(found) < 10 and attempts < 40:
        candidates = generate_pretty_usernames(length, count=30)
        for username in candidates:
            if username in shown_set:
                continue
            if await is_username_free(username):
                found.append(username)
                shown_set.add(username)
                if len(found) >= 10:
                    break
        attempts += 1
    
    await wait_msg.delete()
    
    if not found:
        await message.answer(f"❌ Свободные красивые username для длины {length} закончились. Попробуй другую длину")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="5", callback_data="length_5"),
             InlineKeyboardButton(text="6", callback_data="length_6"),
             InlineKeyboardButton(text="7", callback_data="length_7")]
        ])
        await message.answer("Выбери другую длину:", reply_markup=keyboard)
        return
    
    response = ["✅ Нашёл для тебя:"]
    for i, u in enumerate(found, 1):
        # Простая оценка красоты (длина, наличие гласных и т.п.)
        score = random.randint(70, 100)  # заглушка, можно заменить реальной логикой
        response.append(f"{i}. @{u} (рейтинг красоты: {score}/100)")
    text = "\n".join(response)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Найти ещё", callback_data=f"next_{length}")]
    ])
    await message.answer(text, reply_markup=keyboard)

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())