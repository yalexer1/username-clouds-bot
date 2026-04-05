import random
import string
from typing import List, Set

POPULAR_WORDS = {
    "apple", "brain", "cloud", "dream", "eagle", "flame", "glory", "heart", "ideal", "jolly",
    "karma", "light", "magic", "noble", "ocean", "peace", "queen", "rainy", "smart", "trust",
    "unity", "vivid", "wonder", "xenon", "young", "zebra", "amazing", "beauty", "champion",
    "destiny", "endless", "freedom", "genius", "harmony", "inspire", "justice", "kingdom",
    "liberty", "miracle", "natural", "perfect", "quality", "respect", "serenity", "triumph"
}

CONSONANTS = set("bcdfghjklmnpqrstvwxyz")
VOWELS = set("aeiou")

def generate_cvcvc(length: int) -> str:
    result = []
    for i in range(length):
        if i % 2 == 0:
            result.append(random.choice(list(CONSONANTS)))
        else:
            result.append(random.choice(list(VOWELS)))
    return "".join(result)

def generate_random_letters(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))

def generate_usernames_for_length(length: int, count: int = 10) -> List[str]:
    generated: Set[str] = set()
    candidates = []

    words = [w for w in POPULAR_WORDS if len(w) == length]
    random.shuffle(words)
    candidates.extend(words)

    for _ in range(count * 2):
        candidates.append(generate_cvcvc(length))

    for _ in range(count * 3):
        candidates.append(generate_random_letters(length))

    for cand in candidates:
        if cand not in generated and len(cand) == length and cand.isalpha():
            generated.add(cand)
            if len(generated) >= count:
                break

    while len(generated) < count:
        generated.add(generate_random_letters(length))

    return list(generated)