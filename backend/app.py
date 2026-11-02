import os, re, time, secrets, functools, numpy as np, cv2
from flask import Flask, jsonify, request, session
from itsdangerous import URLSafeTimedSerializer, BadSignature
import database, recommender
from model import EmotionModel, ModelUnavailable, detect_face, CLASSES, HERE

def _secret():
    if os.environ.get("SECRET_KEY"): return os.environ["SECRET_KEY"]
    p = os.path.join(HERE, ".secret_key")  # dev only: random key generated once, gitignored
    if not os.path.exists(p): open(p, "w").write(secrets.token_hex(32))
    return open(p).read().strip()

ORIGINS = {"http://localhost:5173", "http://127.0.0.1:5173"}
app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=5 * 1024 * 1024, SECRET_KEY=_secret(), SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
                  PERMANENT_SESSION_LIFETIME=7 * 24 * 3600)
engine = EmotionModel()
tokens = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="prediction")
_buf = {}

def err(msg, code, **kw): return jsonify(ok=False, error=msg, **kw), code

@app.before_request
def guard():
    o = request.headers.get("Origin")
    if o and o not in ORIGINS and request.method != "GET": return err("Origin not allowed.", 403)
    if request.method == "OPTIONS": return "", 204

@app.after_request
def cors(r):
    o = request.headers.get("Origin")
    if o in ORIGINS:
        r.headers.update({"Access-Control-Allow-Origin": o, "Access-Control-Allow-Credentials": "true", "Vary": "Origin",
                          "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS"})
    return r

def login_required(f):
    @functools.wraps(f)
    def w(*a, **k):
        u = database.get_user(session.get("uid")) if session.get("uid") else None
        if not u:
            session.clear(); return err("Not signed in or session expired.", 401)
        return f(u, *a, **k)
    return w

@app.errorhandler(413)
def too_big(_): return err("Image too large (max 5 MB).", 413)
@app.errorhandler(404)
def nf(_): return err("Not found.", 404)

# ---------- auth ----------
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
def pub(u): return {k: u[k] for k in ("id", "name", "email", "preferred_language")}

@app.post("/api/auth/register")
def register():
    d = request.get_json(silent=True) or {}
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not 2 <= len(name) <= 60: return err("Name must be 2-60 characters.", 400)
    if not EMAIL.match(email): return err("Enter a valid email address.", 400)
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return err("Password needs 8+ characters with letters and numbers.", 400)
    u = database.create_user(name, email, pw)
    if not u: return err("An account with this email already exists.", 409)
    session.clear(); session.permanent = True; session["uid"] = u["id"]
    return jsonify(ok=True, user=pub(u)), 201

@app.post("/api/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    u = database.verify((d.get("email") or "").strip().lower(), d.get("password") or "")
    if not u: return err("Invalid email or password.", 401)
    session.clear(); session.permanent = True; session["uid"] = u["id"]
    return jsonify(ok=True, user=pub(u))

@app.post("/api/auth/logout")
def logout():
    session.clear(); return jsonify(ok=True)

@app.get("/api/auth/me")
@login_required
def me(u): return jsonify(ok=True, user=pub(u))

@app.patch("/api/auth/me")
@login_required
def patch_me(u):
    d = request.get_json(silent=True) or {}
    lang = d.get("preferred_language"); name = (d.get("name") or "").strip() or None
    if lang and lang != "All" and lang not in recommender.LANGUAGES: return err("Unknown language.", 400)
    if name and not 2 <= len(name) <= 60: return err("Name must be 2-60 characters.", 400)
    database.update_user(u["id"], name, lang)
    return jsonify(ok=True, user=pub(database.get_user(u["id"])))

# ---------- model / detection ----------
def _json(name):
    import json; p = os.path.join(HERE, "models", name)
    return json.load(open(p)) if os.path.exists(p) else None

@app.get("/api/health")
def health(): return jsonify(ok=True, status="running")

@app.get("/api/model/status")
def status():
    ok = engine.available()
    return jsonify(ok=True, model_available=ok, classes=CLASSES, metrics=_json("metrics.json"), history=_json("history.json"),
                   message=None if ok else "The trained CNN is not available. Prepare FER-2013 and run train_model.py (see README). Evaluation results are pending.")

@app.post("/api/predict/reset")
@login_required
def reset(u): _buf.pop(u["id"], None); return jsonify(ok=True)

@app.post("/api/predict")
@login_required
def predict(u):
    if not engine.available():
        return err("The trained CNN is unavailable: train the model first (see README).", 503, model_available=False)
    f = request.files.get("image")
    if not f: return err("No webcam frame in request.", 400)
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None or img.size == 0: return err("Frame is not a valid image.", 400)
    try:
        face, box = detect_face(img)
    except Exception as e:
        return err(f"Face detector failed: {e}", 500)
    if face is None: return err("No face detected.", 422, face_detected=False)
    try:
        probs = engine.predict(face)
    except ModelUnavailable as e:
        return err(str(e), 503, model_available=False)
    except Exception as e:
        return err(f"Inference failed: {e}", 500)
    now = time.time()  # smooth over the last 5 valid frames (<8 s old); frame itself is discarded
    b = [(t, p) for t, p in _buf.get(u["id"], []) if now - t < 8][-4:] + [(now, probs)]
    _buf[u["id"]] = b
    avg = {c: sum(p[c] for _, p in b) / len(b) for c in CLASSES}
    top = max(avg, key=avg.get)
    return jsonify(ok=True, source="cnn", box=box, emotion=top, confidence=avg[top], probabilities=avg,
                   token=tokens.dumps({"u": u["id"], "e": top, "c": avg[top]}))

# ---------- music ----------
@app.get("/api/catalogue/options")
def options():
    return jsonify(ok=True, genres=sorted({s["genre"] for s in recommender.CATALOGUE}), languages=["All", *recommender.LANGUAGES],
                   goals=["auto", "match", *recommender.GOALS])

@app.get("/api/catalogue")
def catalogue():
    try: return jsonify(ok=True, songs=recommender.browse(request.args.get("genre"), request.args.get("energy"), request.args.get("language")))
    except ValueError as e: return err(str(e), 400)

@app.post("/api/recommendations")
@login_required
def recs(u):
    d = request.get_json(silent=True) or {}
    try:
        t = tokens.loads(d.get("token") or "", max_age=900)
        if t["u"] != u["id"]: raise BadSignature("user")
    except BadSignature:
        return err("Run webcam detection first: recommendations need a genuine CNN prediction.", 400)
    try:
        r = recommender.recommend(t["e"], d.get("goal"), d.get("genre"), d.get("energy"), d.get("language"))
    except ValueError as e:
        return err(str(e), 400)
    if d.get("save"): database.add(u["id"], t["e"], t["c"], "cnn", r["goal"], [s["id"] for s in r["songs"]])
    return jsonify(ok=True, **r)

# ---------- history ----------
@app.get("/api/history")
@login_required
def hist(u):
    titles = {s["id"]: f'{s["title"]} - {s["artist"]}' for s in recommender.CATALOGUE}
    rows = database.history(u["id"])
    for r in rows: r["song_titles"] = [titles[i] for i in r["songs"] if i in titles]
    return jsonify(ok=True, history=rows)

@app.get("/api/analytics")
@login_required
def analytics(u): return jsonify(ok=True, **database.analytics(u["id"]))

@app.delete("/api/history")
@login_required
def clear(u):
    if request.args.get("confirm") != "true": return err("Add ?confirm=true to confirm deletion.", 400)
    database.clear(u["id"]); return jsonify(ok=True)

if __name__ == "__main__":
    database.init()
    app.run(port=5000, debug=False)
