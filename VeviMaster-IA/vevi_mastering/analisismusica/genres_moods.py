TARGET_GENRES = [
    "pop",
    "rock",
    "hip hop",
    "electronic",
    "classical",
    "jazz",
    "metal",
    "blues",
    "country",
    "reggae",
    "folk",
    "r&b",
    "soul",
    "funk",
    "house",
    "techno",
    "ambient",
    "latin",
    "punk",
    "disco",
    "trap",
    "drill",
    "hyperpop",
    "reggaeton",
]


# Mapeos de sinónimos/variaciones -> género objetivo
GENRE_SYNONYMS = {
    "hip-hop": "hip hop",
    "hiphop": "hip hop",
    "electronica": "electronic",
    "edm": "electronic",
    "drum and bass": "electronic",
    "dnb": "electronic",
    "trap": "trap",
    "trap music": "trap",
    "drill": "drill",
    "uk drill": "drill",
    "hyperpop": "hyperpop",
    "glitchcore": "hyperpop",
    "pc music": "hyperpop",
    "classics": "classical",
    "rnb": "r&b",
    "r&b;": "r&b",
    "rb": "r&b",
    "hard rock": "rock",
    "soft rock": "rock",
    "alt rock": "rock",
    "alternative rock": "rock",
    "indie rock": "rock",
    "indie": "rock",
    "progressive rock": "rock",
    "death metal": "metal",
    "black metal": "metal",
    "heavy metal": "metal",
    "thrash metal": "metal",
    "latin music": "latin",
    "bossa": "latin",
    "salsa": "latin",
    "reggaeton": "reggaeton",
    "reggeton": "reggaeton",
    "dance": "disco",
    "dance pop": "pop",
    "electropop": "pop",
    "house music": "house",
    "tech house": "house",
    "deep house": "house",
    "minimal techno": "techno",
}


# Categorías de estado de ánimo y sinónimos
MOOD_CATEGORIES = [
    "happy",
    "sad",
    "angry",
    "relaxed",
    "energetic",
    "melancholic",
    "romantic",
    "aggressive",
]


MOOD_SYNONYMS = {
    "happy": "happy",
    "joy": "happy",
    "joyful": "happy",
    "party": "energetic",
    "dance": "energetic",
    "energetic": "energetic",
    "upbeat": "energetic",
    "powerful": "energetic",
    "epic": "energetic",
    "sad": "sad",
    "melancholy": "melancholic",
    "melancholic": "melancholic",
    "blue": "sad",
    "angry": "angry",
    "aggressive": "aggressive",
    "relax": "relaxed",
    "relaxed": "relaxed",
    "calm": "relaxed",
    "chill": "relaxed",
    "romantic": "romantic",
    "love": "romantic",
}


from typing import Optional

def normalize_tag(text: str) -> str:
    return (text or "").strip().lower()


def map_genre_tag_to_target(tag: str) -> Optional[str]:
    tag_norm = normalize_tag(tag)
    if tag_norm in TARGET_GENRES:
        return tag_norm
    if tag_norm in GENRE_SYNONYMS:
        return GENRE_SYNONYMS[tag_norm]
    return None


def map_tag_to_mood(tag: str) -> Optional[str]:
    tag_norm = normalize_tag(tag)
    if tag_norm in MOOD_SYNONYMS:
        return MOOD_SYNONYMS[tag_norm]
    # Heurísticos simples por keywords
    if "happy" in tag_norm or "joy" in tag_norm:
        return "happy"
    if "sad" in tag_norm or "blue" in tag_norm:
        return "sad"
    if "calm" in tag_norm or "chill" in tag_norm or "relax" in tag_norm:
        return "relaxed"
    if "angry" in tag_norm:
        return "angry"
    if "energetic" in tag_norm or "party" in tag_norm or "dance" in tag_norm or "upbeat" in tag_norm:
        return "energetic"
    if "romantic" in tag_norm or "love" in tag_norm:
        return "romantic"
    if "aggressive" in tag_norm:
        return "aggressive"
    if "melanch" in tag_norm:
        return "melancholic"
    return None



