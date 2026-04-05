import random
import string
from typing import List, Set

POPULAR_WORDS = {
    "apple", "brain", "cloud", "dream", "eagle", "flame", "glory", "heart", "ideal", "jolly",
    "karma", "light", "magic", "noble", "ocean", "peace", "queen", "rainy", "smart", "trust",
    "unity", "vivid", "wonder", "xenon", "young", "zebra", "amazing", "beauty", "champion",
    "destiny", "endless", "freedom", "genius", "harmony", "inspire", "justice", "kingdom",
    "liberty", "miracle", "natural", "perfect", "quality", "respect", "serenity", "triumph",
    "star", "moon", "sun", "fire", "ice", "dark", "shadow", "storm", "thunder",
    "wild", "cool", "pro", "max", "top", "best", "king", "queen", "lord", "lady", "sir",
    "time", "year", "people", "way", "day", "man", "thing", "woman", "life", "child",
    "world", "school", "state", "family", "student", "group", "country", "problem", "hand", "part",
    "place", "case", "week", "company", "system", "program", "question", "work", "government", "number",
    "night", "point", "home", "water", "room", "mother", "area", "money", "story", "fact",
    "month", "lot", "right", "study", "book", "eye", "job", "word", "business", "issue",
    "side", "kind", "head", "far", "black", "white", "early", "important", "long", "big",
    "small", "old", "good", "bad", "new", "first", "last", "public", "private", "high",
    "low", "large", "little", "same", "different", "next", "other", "own", "sure", "true",
    "whole", "better", "able", "clear", "common", "complete", "easy", "full", "hard", "likely",
    "local", "main", "major", "necessary", "past", "possible", "real", "simple", "single", "special",
    "specific", "strong", "successful", "usual", "younger", "elder", "human", "friend", "love",
    "view", "life", "death", "music", "art", "science", "history", "reading", "writing", "speaking",
    "listening", "learning", "teaching", "building", "creating", "playing", "working", "living", "caring", "sharing",
    "plan", "idea", "change", "move", "stay", "leave", "bring", "take", "give", "receive",
    "find", "lose", "keep", "hold", "let", "allow", "help", "hurt", "like", "dislike",
    "love", "hate", "want", "need", "have", "get", "make", "do", "say", "tell",
    "talk", "speak", "ask", "answer", "call", "write", "read", "listen", "hear", "see",
    "watch", "look", "feel", "think", "believe", "know", "understand", "remember", "forget", "decide",
    "choose", "start", "begin", "end", "finish", "continue", "stop", "wait", "stay", "live",
    "die", "kill", "save", "protect", "attack", "fight", "win", "lose", "play", "work",
    "study", "learn", "teach", "explain", "show", "tell", "give", "take", "use", "make",
    "create", "build", "destroy", "break", "fix", "repair", "clean", "wash", "dry", "wet",
    "open", "close", "enter", "exit", "come", "go", "arrive", "leave", "return", "send",
    "receive", "buy", "sell", "pay", "cost", "spend", "save", "earn", "lose", "find",
    "search", "look", "see", "watch", "observe", "notice", "ignore", "avoid", "accept", "refuse",
    "allow", "forbid", "permit", "ban", "agree", "disagree", "argue", "discuss", "talk", "speak",
    "shout", "whisper", "cry", "laugh", "smile", "frown", "look", "listen", "hear", "touch",
    "feel", "smell", "taste", "see", "watch", "observe", "notice", "ignore", "avoid", "accept",
    "refuse", "allow", "forbid", "permit", "ban", "agree", "disagree", "argue", "discuss", "talk",
    "speak", "shout", "whisper", "cry", "laugh", "smile", "frown", "wink", "blink", "sleep",
    "wake", "dream", "imagine", "create", "design", "draw", "paint", "sing", "dance", "jump",
    "run", "walk", "fly", "swim", "drive", "ride", "climb", "fall", "drop", "catch",
    "throw", "push", "pull", "lift", "carry", "hold", "grab", "release", "open", "close",
    "lock", "unlock", "turn", "twist", "bend", "stretch", "break", "crack", "smash", "crush",
    "cut", "slice", "chop", "stab", "pierce", "penetrate", "enter", "exit", "approach", "leave",
    "arrive", "depart", "stay", "remain", "continue", "stop", "pause", "resume", "start", "begin",
    "end", "finish", "complete", "terminate", "cancel", "delete", "remove", "add", "insert", "include",
    "exclude", "join", "separate", "divide", "split", "share", "distribute", "collect", "gather", "assemble",
    "build", "construct", "erect", "raise", "lift", "lower", "drop", "fall", "sink", "float",
    "fly", "soar", "glide", "slide", "slip", "trip", "stumble", "fall", "drop", "catch",
    "throw", "toss", "fling", "hurl", "launch", "shoot", "fire", "blast", "explode", "implode",
    "collapse", "crumble", "disintegrate", "vanish", "appear", "emerge", "surface", "hide", "conceal", "reveal",
    "show", "display", "exhibit", "demonstrate", "prove", "disprove", "confirm", "deny", "affirm", "negate",
    "support", "oppose", "resist", "comply", "obey", "disobey", "follow", "lead", "guide", "direct",
    "control", "manage", "supervise", "monitor", "watch", "guard", "protect", "defend", "attack", "strike",
    "hit", "beat", "punch", "kick", "slap", "scratch", "bite", "chew", "swallow", "digest",
    "absorb", "excrete", "breathe", "inhale", "exhale", "cough", "sneeze", "yawn", "stretch", "exercise",
    "privet", "poka", "spasibo", "pozhaluysta", "izvinite", "zdravstvuyte", "dobroye_utro", "dobryy_den", "dobryy_vecher", "spokoynoy_nochi",
    "kak_dela", "normalno", "horosho", "ploho", "otlichno", "uzhasno", "interesno", "skuchno", "veselo", "grustno",
    "mama", "papa", "brat", "sestra", "babushka", "dedushka", "syn", "doch", "vnuk", "vnuchka",
    "dyadya", "tyotya", "drug", "podruga", "sosed", "kollega", "nachalnik", "rabochiy", "uchitel", "uchenik",
    "vrach", "medsestra", "pozharnyy", "policeyskiy", "prodavets", "pokupatel", "voditel", "passazhir", "pilot", "styuardessa",
    "dom", "kvartira", "komnata", "kuhnya", "vannaya", "tualet", "balkon", "podval", "cherdak", "dvor",
    "ulitsa", "prospekt", "pereezd", "perekrestok", "svetofor", "zebra", "trotuar", "most", "park", "skver",
    "magazin", "rynok", "torgovyy_tsentr", "apteka", "bolnitsa", "poliklinika", "shkola", "universitet", "biblioteka", "kafe",
    "restoran", "bar", "klub", "kino", "teatr", "muzy", "stadion", "basseyn", "sportzal", "trenazherka",
    "rabota", "ofis", "zavod", "fabrika", "stroyka", "ferma", "bank", "pochtamt", "politsiya", "sud",
    "tюрьма", "svoboda", "pravo", "zakon", "prestupleniye", "shtraf", "nalog", "dengi", "rubl", "dollar",
    "yevro", "zarplata", "premiya", "pensiya", "stipendiya", "kredit", "dolg", "oplata", "chek", "kopeyka",
    "eda", "voda", "khleb", "maslo", "syry", "myaso", "kury", "ryba", "ovoshchi", "frukty",
    "yabloko", "apelsin", "banan", "limon", "vinograd", "arbuz", "dynya", "klubnika", "malina", "vishnya",
    "kartoshka", "morkov", "luk", "chesnok", "kapusta", "ogurets", "pomidor", "perets", "baklazhan", "kabachok",
    "chay", "kofe", "sok", "kompot", "kisel", "limonad", "pivo", "vino", "vodka", "konyak",
    "sredstvo", "mylo", "shampun", "pasta", "polotentse", "gubka", "shchyotka", "venik", "sovok", "vedro",
    "stol", "stul", "divan", "krovat", "shkaf", "polka", "zerkalo", "lampa", "lyustra", "kovyor",
    "okno", "dver", "klyuch", "zamok", "ruчка", "karandash", "kniga", "tetrad", "dnevnik", "telefon",
    "kompyuter", "klaviatura", "mish", "ekran", "naushniki", "zaryadka", "batareya", "provod", "usb", "wi-fi",
    "mashina", "avtobus", "tramvay", "trolleybus", "metro", "poezd", "samolet", "korabl", "velosiped", "mototsikl",
    "doroga", "trassa", "most", "tonnel", "svet", "ten", "solntse", "luna", "zvezda", "nebo",
    "oblako", "dozhd", "sneg", "grad", "veter", "shtorm", "grom", "molniya", "raina", "zima",
    "vesna", "leto", "osen", "den", "noch", "utro", "vecher", "polnoch", "poluden", "chas",
    "minuta", "sekunda", "nedelya", "mesyats", "god", "vek", "sutki", "vechnost", "seychas", "potom",
    "zavtra", "vchera", "segodnya", "segodnya", "rano", "pozdno", "vsegda", "nikogda", "chasto", "redko",
    "mnogo", "malo", "skolko", "stolko", "bolshoy", "malenkiy", "vysokiy", "nizkiy", "shirokiy", "uzkiy",
    "dlinniy", "korotkiy", "tolstyy", "tonkiy", "tyazhelyy", "lyogkiy", "novyy", "staryy", "molodoy", "poyiloy",
    "krasivyy", "straшnyy", "dobryy", "zloy", "umnyy", "glupyy", "vesyolyy", "grustnyy", "bogatyy", "bednyy",
    "eblan", "pizdec", "blyad", "huiny", "nahuy", "pizda", "huy", "mudak", "dolboyob", "gandon",
    "shlyuha", "prostitutka", "suka", "ublyudok", "pidoras", "petuh", "loh", "razvod", "razvodila", "kishmish",
    "shmon", "obnak", "bazar", "bablos", "koshmar", "bespredel", "kipish", "tusovka", "otmorozok", "byk",
    "bratva", "beshenyy", "priton", "fart", "ksiva", "ment", "musor", "leavy", "shnyaga", "bochka",
    "drakon", "bayan", "banan", "samsung", "nokia", "iphone", "android", "windows", "linux", "google",
    "yandex", "mail", "vk", "odnoklassniki", "instagram", "facebook", "twitter", "tiktok", "youtube", "telega",
    "chemodan", "vokzal", "samolet", "poyezd", "bilet", "kassa", "bagazh", "russa", "puteshestvie", "otpusk",
    "biznes", "firma", "klient", "dogovor", "schet", "nalichka", "beznal", "kartochka", "terminal", "bankomat",
    "kredit", "ipoteka", "zayom", "procent", "strahovka", "nalogi", "buhgalter", "direktor", "zavedyushiy", "ohrana",
    "remont", "master", "instrument", "gvozd", "shurup", "bolt", "gayka", "otvertka", "molotok", "pilka",
    "bumaga", "pis'mo", "konvert", "marka", "posylka", "bank", "otpravit", "poluchit", "adres", "index",
    "avtor", "podpis", "shtamp", "pechat"
}

CONSONANTS = list("bcdfghjklmnpqrstvwxyz")
VOWELS = list("aeiou")
SUFFIXES = ["er", "ly", "ing", "y", "ic", "al", "ous", "ive", "ful", "ish"]

def generate_cvcvc(length: int) -> str:
    return ''.join(random.choice(CONSONANTS) if i%2==0 else random.choice(VOWELS) for i in range(length))

def generate_with_suffix(word: str, length: int) -> str:
    if len(word) >= length:
        return word[:length]
    suffix = random.choice(SUFFIXES)
    new = (word + suffix)[:length]
    return new if len(new) == length else word

def generate_leet(word: str) -> str:
    leet_map = {'a':'4','e':'3','i':'1','o':'0','s':'5'}
    return ''.join(leet_map.get(ch, ch) for ch in word)

def generate_random_letters(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_usernames_for_length(length: int, count: int = 100) -> List[str]:
    generated = set()
    candidates = []

    words = [w for w in POPULAR_WORDS if len(w) == length]
    random.shuffle(words)
    candidates.extend(words[:count//3])

    for w in list(POPULAR_WORDS)[:count]:
        if len(w) <= length - 2:
            candidates.append(generate_with_suffix(w, length))

    for w in list(POPULAR_WORDS)[:count]:
        if len(w) == length:
            leeted = generate_leet(w)
            if leeted != w:
                candidates.append(leeted)

    for _ in range(count):
        candidates.append(generate_cvcvc(length))

    for _ in range(count):
        candidates.append(generate_random_letters(length))

    for c in candidates:
        if c not in generated and len(c)==length and c.islower():
            generated.add(c)
            if len(generated) >= count:
                break

    while len(generated) < count:
        generated.add(generate_random_letters(length))

    return list(generated)