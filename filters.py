import re
from generator import POPULAR_WORDS, CONSONANTS, VOWELS

def is_word(word: str) -> bool:
    return word.lower() in POPULAR_WORDS

def is_cvcvc_pattern(username: str) -> bool:
    for i, ch in enumerate(username):
        if i % 2 == 0:
            if ch not in CONSONANTS:
                return False
        else:
            if ch not in VOWELS:
                return False
    return True

def has_repeating_letters(username: str) -> bool:
    return bool(re.search(r'(.)\1', username))

def max_consecutive_consonants(username: str) -> int:
    max_run = 0
    current = 0
    for ch in username:
        if ch in CONSONANTS:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

def leet_to_word(username: str) -> str:
    mapping = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's'}
    converted = []
    for ch in username:
        converted.append(mapping.get(ch, ch))
    return "".join(converted)

def calculate_beauty_score(username: str) -> int:
    score = 0
    original = username.lower()

    if is_word(original):
        score += 50
    if is_cvcvc_pattern(original):
        score += 40
    if has_repeating_letters(original):
        score += 20
    if max_consecutive_consonants(original) <= 2:
        score += 15
    leet_converted = leet_to_word(original)
    if leet_converted != original and is_word(leet_converted):
        score += 30
    if original.isalpha():
        score += 10

    return min(score, 100)