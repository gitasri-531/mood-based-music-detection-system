"""Deterministic, explainable tag-overlap recommender. Rules are heuristic, not scientific facts."""
from urllib.parse import quote_plus

def _s(i, title, artist, genre, lang, energy, tags):
    # Links are YouTube *search* URLs (valid endpoint, built from title+artist). Direct video URLs are not
    # invented; replace with verified official links in this catalogue if you want to.
    return dict(id=i, title=title, artist=artist, genre=genre, language=lang, energy=energy, tags=tags,
                source="YouTube search", link="https://www.youtube.com/results?search_query=" + quote_plus(f"{title} {artist} official"))

CATALOGUE = [
    _s(1, 'Happy', 'Pharrell Williams', 'Pop', 'English', 'high', ['upbeat', 'energetic', 'uplifting']),
    _s(2, 'Dont Stop Me Now', 'Queen', 'Rock', 'English', 'high', ['energetic', 'upbeat', 'lively']),
    _s(3, 'Walking on Sunshine', 'Katrina and the Waves', 'Pop', 'English', 'high', ['upbeat', 'uplifting']),
    _s(4, 'Weightless', 'Marconi Union', 'Ambient', 'Instrumental', 'low', ['calm', 'gentle', 'reassuring']),
    _s(5, 'Clair de Lune', 'Claude Debussy', 'Classical', 'Instrumental', 'low', ['calm', 'gentle', 'reflective']),
    _s(6, 'Here Comes the Sun', 'The Beatles', 'Rock', 'English', 'medium', ['uplifting', 'gentle', 'upbeat']),
    _s(7, 'Lean on Me', 'Bill Withers', 'Soul', 'English', 'medium', ['comforting', 'uplifting', 'reassuring']),
    _s(8, 'Fix You', 'Coldplay', 'Alternative', 'English', 'medium', ['comforting', 'uplifting', 'reflective']),
    _s(9, 'Eye of the Tiger', 'Survivor', 'Rock', 'English', 'high', ['energetic', 'lively']),
    _s(10, 'Lose Yourself', 'Eminem', 'Hip-hop', 'English', 'high', ['energetic', 'focus']),
    _s(11, 'Three Little Birds', 'Bob Marley', 'Reggae', 'English', 'low', ['reassuring', 'gentle', 'uplifting', 'calm']),
    _s(12, 'Holocene', 'Bon Iver', 'Indie', 'English', 'low', ['reflective', 'calm', 'comforting']),
    _s(13, 'Experience', 'Ludovico Einaudi', 'Classical', 'Instrumental', 'medium', ['focus', 'balanced', 'reflective']),
    _s(14, 'Intro', 'The xx', 'Indie', 'Instrumental', 'low', ['balanced', 'focus', 'chill']),
    _s(15, 'Africa', 'Toto', 'Rock', 'English', 'medium', ['lively', 'balanced', 'upbeat']),
    _s(16, 'Dancing Queen', 'ABBA', 'Pop', 'English', 'high', ['lively', 'upbeat']),
    _s(17, 'Butta Bomma', 'Armaan Malik', 'Film', 'Telugu', 'high', ['upbeat', 'lively']),
    _s(18, 'Samajavaragamana', 'Sid Sriram', 'Film', 'Telugu', 'low', ['calm', 'gentle', 'comforting', 'balanced']),
    _s(19, 'Naatu Naatu', 'Rahul Sipligunj, Kaala Bhairava', 'Film', 'Telugu', 'high', ['energetic', 'lively', 'upbeat']),
    _s(20, 'Ramuloo Ramulaa', 'Anurag Kulkarni, Mangli', 'Film', 'Telugu', 'high', ['energetic', 'lively', 'upbeat']),
    _s(21, 'Inkem Inkem Inkem Kaavaale', 'Sid Sriram', 'Film', 'Telugu', 'low', ['calm', 'gentle', 'chill', 'reassuring']),
    _s(22, 'Srivalli', 'Sid Sriram', 'Film', 'Telugu', 'medium', ['reflective', 'comforting', 'gentle']),
    _s(23, 'Oo Antava', 'Indravathi Chauhan', 'Film', 'Telugu', 'high', ['energetic', 'lively']),
    _s(24, 'Nee Kannu Neeli Samudram', 'Javed Ali', 'Film', 'Telugu', 'low', ['calm', 'reflective', 'comforting', 'gentle']),
    _s(25, 'Mind Block', 'Blaaze, Ranina Reddy', 'Film', 'Telugu', 'high', ['energetic', 'focus', 'uplifting']),
    _s(26, 'Kun Faya Kun', 'A. R. Rahman, Javed Ali, Mohit Chauhan', 'Sufi', 'Hindi', 'low', ['calm', 'reflective', 'comforting', 'gentle']),
    _s(27, 'Badtameez Dil', 'Benny Dayal', 'Film', 'Hindi', 'high', ['upbeat', 'energetic', 'lively']),
    _s(28, 'Tum Hi Ho', 'Arijit Singh', 'Film', 'Hindi', 'low', ['comforting', 'reflective', 'calm']),
    _s(29, 'Kabira', 'Tochi Raina, Rekha Bhardwaj', 'Film', 'Hindi', 'medium', ['reflective', 'comforting', 'uplifting', 'reassuring']),
    _s(30, 'Channa Mereya', 'Arijit Singh', 'Film', 'Hindi', 'low', ['reflective', 'comforting']),
    _s(31, 'Ilahi', 'Arijit Singh', 'Film', 'Hindi', 'medium', ['uplifting', 'upbeat', 'gentle', 'balanced']),
    _s(32, 'Kar Har Maidaan Fateh', 'Sukhwinder Singh, Shreya Ghoshal', 'Film', 'Hindi', 'high', ['energetic', 'focus', 'uplifting']),
    _s(33, 'Chaiyya Chaiyya', 'Sukhwinder Singh, Sapna Awasthi', 'Film', 'Hindi', 'high', ['energetic', 'lively', 'upbeat']),
    _s(34, 'Dil Chahta Hai', 'Shankar Mahadevan', 'Film', 'Hindi', 'medium', ['balanced', 'chill', 'uplifting']),
    _s(35, 'Kesariya', 'Arijit Singh', 'Film', 'Hindi', 'low', ['gentle', 'reassuring', 'chill', 'balanced']),
    _s(36, 'Apna Time Aayega', 'Ranveer Singh', 'Hip-hop', 'Hindi', 'high', ['energetic', 'focus']),
]
LANGUAGES = ["Telugu", "Hindi", "English"]
EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
# Editable rules: what "match my expression" means per class.
MATCH = {"happy": ["upbeat", "energetic"], "sad": ["comforting", "reflective"], "angry": ["energetic", "focus"],
         "neutral": ["balanced", "focus", "chill"], "surprise": ["lively", "upbeat"],
         "fear": ["gentle", "reassuring"], "disgust": ["reflective", "calm"]}
GOALS = {"relax": ["calm", "gentle"], "energize": ["energetic", "lively"],
         "uplift": ["uplifting", "upbeat"], "comfort": ["comforting", "reassuring"]}
DEFAULT_GOAL = {"happy": "match", "sad": "comfort", "angry": "relax", "neutral": "match",
                "surprise": "match", "fear": "comfort", "disgust": "relax"}

def _lang_ok(song, language):
    if not language or language == "All": return True
    return song["language"] == language or (language == "English" and song["language"] == "Instrumental")

def _filter(genre, energy, language):
    if language and language != "All" and language not in LANGUAGES:
        raise ValueError(f"Unknown language '{language}'")
    return [s for s in CATALOGUE if _lang_ok(s, language) and (not genre or s["genre"].lower() == genre.lower())
            and (not energy or s["energy"] == energy.lower())]

def browse(genre=None, energy=None, language=None):
    return [dict(s) for s in _filter(genre, energy, language)]

def recommend(emotion, goal=None, genre=None, energy=None, language=None, limit=8):
    emotion = (emotion or "").lower()
    if emotion not in EMOTIONS: raise ValueError(f"Unknown emotion '{emotion}'")
    goal = (goal or "auto").lower()
    if goal == "auto": goal = DEFAULT_GOAL[emotion]
    if goal != "match" and goal not in GOALS: raise ValueError(f"Unknown goal '{goal}'")
    wanted = MATCH[emotion] if goal == "match" else GOALS[goal]
    out = []
    for s in _filter(genre, energy, language):
        hits = [t for t in wanted if t in s["tags"]]
        if hits:
            out.append(dict(s, score=len(hits), reason=f"Goal '{goal}' for predicted '{emotion}': matches {', '.join(hits)}"))
    out.sort(key=lambda s: (-s["score"], s["id"]))
    return {"emotion": emotion, "goal": goal, "language": language or "All", "songs": out[:limit]}
