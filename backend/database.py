import os, json, sqlite3, datetime
from contextlib import closing
from werkzeug.security import generate_password_hash, check_password_hash

def _path():
    return os.environ.get("MOOD_DB", os.path.join(os.path.dirname(__file__), "mood_history.db"))

def _run(sql, args=(), fetch=False):
    with closing(sqlite3.connect(_path())) as c:
        c.row_factory = sqlite3.Row
        c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, preferred_language TEXT DEFAULT 'All', created TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, emotion TEXT, confidence REAL, source TEXT, goal TEXT, songs TEXT)")
        if "user_id" not in [r[1] for r in c.execute("PRAGMA table_info(history)")]:  # backward-compatible migration
            c.execute("ALTER TABLE history ADD COLUMN user_id INTEGER")
        cur = c.execute(sql, args)
        rows = [dict(r) for r in cur.fetchall()] if fetch else cur.lastrowid
        c.commit()
        return rows

def init(): _run("SELECT 1")

def _public(u):
    return {k: u[k] for k in ("id", "name", "email", "preferred_language")} if u else None

def create_user(name, email, password):
    if get_by_email(email): return None
    _run("INSERT INTO users(name,email,password_hash,created) VALUES(?,?,?,?)",
         (name, email, generate_password_hash(password), datetime.datetime.now().isoformat(timespec="seconds")))
    return get_by_email(email)

def get_by_email(email):
    r = _run("SELECT * FROM users WHERE email=?", (email,), True); return r[0] if r else None

def get_user(uid):
    r = _run("SELECT * FROM users WHERE id=?", (uid,), True); return r[0] if r else None

def verify(email, password):
    u = get_by_email(email)
    return u if u and check_password_hash(u["password_hash"], password) else None

def update_user(uid, name=None, lang=None):
    if name: _run("UPDATE users SET name=? WHERE id=?", (name, uid))
    if lang: _run("UPDATE users SET preferred_language=? WHERE id=?", (lang, uid))

def add(uid, emotion, confidence, source, goal, song_ids):
    _run("INSERT INTO history(user_id,ts,emotion,confidence,source,goal,songs) VALUES(?,?,?,?,?,?,?)",
         (uid, datetime.datetime.now().isoformat(timespec="seconds"), emotion, confidence, source, goal, json.dumps(song_ids)))

def history(uid, limit=100):
    rows = _run("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, limit), True)
    for r in rows: r["songs"] = json.loads(r["songs"] or "[]")
    return rows

def analytics(uid):
    dist = _run("SELECT emotion, COUNT(*) n FROM history WHERE user_id=? GROUP BY emotion", (uid,), True)
    daily = _run("SELECT substr(ts,1,10) day, COUNT(*) n FROM history WHERE user_id=? GROUP BY day ORDER BY day", (uid,), True)
    return {"total": sum(d["n"] for d in dist), "distribution": dist, "daily": daily}

def clear(uid): _run("DELETE FROM history WHERE user_id=?", (uid,))
