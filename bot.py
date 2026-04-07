import asyncio
import os
import random
from typing import Dict, List, Tuple
from enum import Enum
from threading import Thread
from flask import Flask, request
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import aiohttp
from bs4 import BeautifulSoup

load_dotenv()

# ========== КОНФИГУРАЦИЯ ==========
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
STRING_SESSION = os.getenv("STRING_SESSION")  # Добавляем строку сессии

# Flask приложение для веб-сервера
app = Flask(__name__)

# Список красивых английских слов
POPULAR_WORDS = {
    "dream", "cloud", "star", "moon", "sun", "sky", "blue", "red", "green", "gold",
    "rose", "love", "hope", "peace", "happy", "smart", "cool", "nice", "good", "best",
    "king", "queen", "lord", "lady", "hero", "epic", "pro", "max", "top", "win",
    "art", "soul", "heart", "mind", "brain", "fire", "water", "earth", "air", "wind",
    "rain", "snow", "ice", "hot", "cold", "new", "old", "young", "fast", "slow",
    "big", "small", "tall", "short", "long", "wide", "deep", "high", "low", "light",
    "dark", "bright", "soft", "hard", "sweet", "sour", "bitter", "fresh", "clean",
    "pure", "simple", "easy", "hard", "rich", "poor", "strong", "weak", "brave",
    "calm", "wild", "free", "true", "real", "fake", "rare", "common", "unique",
    "special", "great", "awesome", "amazing", "wonder", "magic", "myth", "legend"
}

VOWELS = set('aeiou')
CONSONANTS = set('bcdfghjklmnpqrstvwxyz')

class UsernameStatus(Enum):
    FREE = "free"
    TAKEN = "taken"
    AUCTION = "auction"

# Кэш для сессий пользователей
user_sessions: Dict[int, Dict] = {}

# ========== ФУНКЦИИ ОЦЕНКИ КРАСОТЫ ==========

def is_cvcvc_pattern(username: str) -> bool:
    if len(username) < 5:
        return False
    username = username.lower()
    for i, ch in enumerate(username[:5]):
        if i % 2 == 0:
            if ch not in CONSONANTS:
                return False
        else:
            if ch not in VOWELS:
                return False
    return True

def has_repeating_letters(username: str) -> bool:
    username = username.lower()
    for i in range(len(username) - 1):
        if username[i] == username[i + 1]:
            return True
    return False

def is_easily_readable(username: str) -> bool:
    username = username.lower()
    consonant_run = 0
    for ch in username:
        if ch in CONSONANTS:
            consonant_run += 1
            if consonant_run > 2:
                return False
        else:
            consonant_run = 0
    return True

def leet_to_word(username: str) -> str:
    leet_map = {
        '4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's',
        '@': 'a', '$': 's', '7': 't', '8': 'b', '9': 'g'
    }
    return ''.join(leet_map.get(ch, ch) for ch in username.lower())

def is_leet_word(username: str) -> Tuple[bool, str]:
    decoded = leet_to_word(username)
    if decoded in POPULAR_WORDS:
        return True, decoded
    if decoded.isalpha() and len(decoded) >= 3:
        return True, decoded
    return False, ""

def is_dictionary_word(username: str) -> bool:
    return username.lower() in POPULAR_WORDS

def has_no_digits(username: str) -> bool:
    return not any(ch.isdigit() for ch in username)

def calculate_beauty_score(username: str) -> Tuple[int, List[str]]:
    score = 0
    reasons = []
    username_lower = username.lower()
    
    if is_dictionary_word(username_lower):
        score += 50
        reasons.append("словарное слово")
    
    if is_cvcvc_pattern(username_lower):
        score += 40
        reasons.append("паттерн CVCVC")
    
    if has_repeating_letters(username_lower):
        score += 20
        reasons.append("повторяющиеся буквы")
    
    if is_easily_readable(username_lower):
        score += 15
        reasons.append("легко читаемый")
    
    is_leet, leet_word = is_leet_word(username)
    if is_leet:
        score += 30
        reasons.append(f"leet-speak ({leet_word})")
    
    if has_no_digits(username):
        score += 10
        reasons.append("без цифр")
    
    score = min(score, 100)
    return score, reasons

# ========== ПРОВЕРКА ДОСТУПНОСТИ ==========

async def check_mtproto_username(client: Client, username: str) -> bool:
    try:
        user = await client.resolve_username(username)
        return user is None
    except Exception as e:
        if "USERNAME_NOT_OCCUPIED" in str(e):
            return True
        return False

async def check_fragment_username(username: str) -> UsernameStatus:
    url = f"https://fragment.com/username/{username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return UsernameStatus.FREE
                html = await response.text()
                text = html.lower()
                if "place a bid" in text or "auction" in text:
                    return UsernameStatus.AUCTION
                return UsernameStatus.FREE
    except Exception:
        return UsernameStatus.FREE

async def is_username_free(client: Client, username: str) -> Tuple[bool, UsernameStatus]:
    mtproto_free = await check_mtproto_username(client, username)
    if not mtproto_free:
        return False, UsernameStatus.TAKEN
    
    fragment_status = await check_fragment_username(username)
    if fragment_status == UsernameStatus.AUCTION:
        return False, UsernameStatus.AUCTION
    
    return True, UsernameStatus.FREE

# ========== ГЕНЕРАЦИЯ USERNAME ==========

def generate_random_username(length: int) -> str:
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(letters) for _ in range(length))

def generate_cvcvc_username(length: int) -> str:
    if length == 5:
        return (random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)))
    elif length == 6:
        return (random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)))
    elif length == 7:
        return (random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) + 
                random.choice(list(CONSONANTS)) + random.choice(list(VOWELS)) +
                random.choice(list(CONSONANTS)))
    return generate_random_username(length)

def generate_word_based_username(length: int) -> str:
    possible_words = [w for w in POPULAR_WORDS if len(w) <= length]
    if not possible_words:
        return generate_random_username(length)
    
    word = random.choice(possible_words)
    if len(word) == length:
        return word
    elif len(word) < length:
        extra = length - len(word)
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return word + ''.join(random.choice(letters) for _ in range(extra))
    else:
        return word[:length]

async def find_beautiful_usernames(
    client: Client, 
    length: int, 
    limit: int = 10,
    exclude: List[str] = None
) -> List[Tuple[str, int, str]]:
    if exclude is None:
        exclude = []
    
    found = []
    attempts = 0
    max_attempts = 500
    
    while len(found) < limit and attempts < max_attempts:
        attempts += 1
        
        strategy = random.choice(['random', 'cvcvc', 'word'])
        if strategy == 'cvcvc':
            username = generate_cvcvc_username(length)
        elif strategy == 'word':
            username = generate_word_based_username(length)
        else:
            username = generate_random_username(length)
        
        if username in exclude or any(u[0] == username for u in found):
            continue
        
        score, reasons = calculate_beauty_score(username)
        
        if score >= 70:
            is_free, status = await is_username_free(client, username)
            if is_free:
                reason_str = ", ".join(reasons[:2])
                found.append((username, score, reason_str))
                print(f"Found: @{username} (score: {score})")
    
    found.sort(key=lambda x: x[1], reverse=True)
    return found[:limit]

# ========== КЛАВИАТУРЫ ==========

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Искать username", callback_data="search"),
            InlineKeyboardButton("👤 Кто создатель?", callback_data="creator")
        ]
    ])

def get_length_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5", callback_data="length_5"),
            InlineKeyboardButton("6", callback_data="length_6"),
            InlineKeyboardButton("7", callback_data="length_7")
        ]
    ])

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]
    ])

def get_find_more_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Найти ещё", callback_data="find_more")]
    ])

# ========== ОСНОВНОЙ КОД БОТА ==========

# Создаем клиент для бота
bot_app = Client(
    "username_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Создаем клиент для пользователя (для проверки username)
# Используем строку сессии, если она есть, иначе phone_number
if STRING_SESSION:
    print("✅ Используем строку сессии для авторизации")
    user_client = Client(
        "user_session",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION
    )
else:
    print("⚠️ Строка сессии не найдена, используем номер телефона")
    user_client = Client(
        "user_session",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )

@bot_app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply(
        "Добро пожаловать в Username Clouds☁, тут вы можете найти красивые username",
        reply_markup=get_main_keyboard()
    )

@bot_app.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "current_length": None,
            "found_usernames": []
        }
    
    if data == "creator":
        await callback_query.message.edit_text(
            "Мой создатель - t.me/savesep",
            reply_markup=get_back_keyboard()
        )
    
    elif data == "back_to_main":
        await callback_query.message.edit_text(
            "Добро пожаловать в Username Clouds☁, тут вы можете найти красивые username",
            reply_markup=get_main_keyboard()
        )
    
    elif data == "search":
        await callback_query.message.edit_text(
            "Выбери длину username для поиска:",
            reply_markup=get_length_keyboard()
        )
    
    elif data.startswith("length_"):
        length = int(data.split("_")[1])
        user_sessions[user_id]["current_length"] = length
        user_sessions[user_id]["found_usernames"] = []
        
        await callback_query.message.edit_text(
            f"🔎 Ищу красивые свободные username из {length} букв... Это может занять несколько секунд",
            reply_markup=None
        )
        
        found = await find_beautiful_usernames(
            user_client, 
            length, 
            limit=10,
            exclude=[]
        )
        
        if found:
            user_sessions[user_id]["found_usernames"] = [u[0] for u in found]
            
            result_text = "✅ Нашёл для тебя:\n"
            for i, (username, score, reason) in enumerate(found, 1):
                result_text += f"{i}. @{username} (рейтинг красоты: {score}/100)\n"
            
            await callback_query.message.edit_text(
                result_text,
                reply_markup=get_find_more_keyboard()
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Не удалось найти красивые свободные username для длины {length}. Попробуй другую длину.",
                reply_markup=get_length_keyboard()
            )
    
    elif data == "find_more":
        length = user_sessions[user_id].get("current_length")
        exclude = user_sessions[user_id].get("found_usernames", [])
        
        if not length:
            await callback_query.answer("Пожалуйста, начните поиск заново")
            return
        
        await callback_query.message.edit_text(
            f"🔎 Ищу ещё красивые свободные username из {length} букв...",
            reply_markup=None
        )
        
        found = await find_beautiful_usernames(
            user_client,
            length,
            limit=10,
            exclude=exclude
        )
        
        if found:
            user_sessions[user_id]["found_usernames"].extend([u[0] for u in found])
            
            result_text = "✅ Нашёл для тебя:\n"
            for i, (username, score, reason) in enumerate(found, 1):
                result_text += f"{i}. @{username} (рейтинг красоты: {score}/100)\n"
            
            await callback_query.message.edit_text(
                result_text,
                reply_markup=get_find_more_keyboard()
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Свободные красивые username для длины {length} закончились. Попробуй другую длину",
                reply_markup=get_length_keyboard()
            )
    
    await callback_query.answer()

@app.route('/')
def health_check():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return {"status": "ok"}

def run_bot():
    """Запуск бота в отдельном потоке"""
    async def start_clients():
        await user_client.start()
        print("✅ User client запущен")
        await bot_app.start()
        print("✅ Бот запущен!")
        await asyncio.Event().wait()
    
    asyncio.run(start_clients())

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер для health check
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)