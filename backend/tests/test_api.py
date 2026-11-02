import os, sys, tempfile, unittest, io, sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["SECRET_KEY"] = "test-secret"
os.environ["MOOD_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
import numpy as np, cv2
import app as A, model, recommender, database

PW = "Passw0rdOK"
def frame(): return io.BytesIO(cv2.imencode(".png", np.full((120, 120, 3), 127, np.uint8))[1].tobytes())
def user(n):
    c = A.app.test_client()
    r = c.post("/api/auth/register", json={"name": "User " + n, "email": f"{n}@x.com", "password": PW}); assert r.status_code == 201, r.json
    return c

class FakeKeras:
    def predict(self, x, verbose=0):
        assert x.shape == (1, 48, 48, 1)
        p = np.zeros((1, 7)); p[0, 3] = 0.9; p[0, 5] = 0.1; return p

class Auth(unittest.TestCase):
    def test_register_login_logout(self):
        c = user("a1"); r = c.get("/api/auth/me"); self.assertEqual(r.json["user"]["email"], "a1@x.com")
        self.assertNotIn("password", str(r.json).lower())
        c.post("/api/auth/logout"); self.assertEqual(c.get("/api/auth/me").status_code, 401)
        self.assertEqual(A.app.test_client().post("/api/auth/login", json={"email": "a1@x.com", "password": "wrong"}).status_code, 401)
        self.assertEqual(A.app.test_client().post("/api/auth/login", json={"email": "a1@x.com", "password": PW}).status_code, 200)
    def test_validation_and_duplicate(self):
        c = A.app.test_client(); user("dup")
        self.assertEqual(c.post("/api/auth/register", json={"name": "D", "email": "dup@x.com", "password": PW}).status_code, 400)
        self.assertEqual(c.post("/api/auth/register", json={"name": "Dup", "email": "bad", "password": PW}).status_code, 400)
        self.assertEqual(c.post("/api/auth/register", json={"name": "Dup", "email": "d@x.com", "password": "short"}).status_code, 400)
        self.assertEqual(c.post("/api/auth/register", json={"name": "Dup", "email": "DUP@x.com", "password": PW}).status_code, 409)
    def test_password_hashed(self):
        h = database.create_user("Hash", "hash@x.com", PW)
        self.assertNotEqual(h["password_hash"], PW); self.assertTrue(h["password_hash"].startswith(("scrypt", "pbkdf2")))
    def test_protected(self):
        c = A.app.test_client()
        for m, p in [("get", "/api/history"), ("get", "/api/analytics"), ("delete", "/api/history?confirm=true"), ("post", "/api/predict"), ("post", "/api/recommendations")]:
            self.assertEqual(getattr(c, m)(p).status_code, 401, p)
    def test_legacy_migration(self):
        p = os.path.join(tempfile.mkdtemp(), "old.db"); k = os.environ["MOOD_DB"]
        con = sqlite3.connect(p); con.execute("CREATE TABLE history(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, emotion TEXT, confidence REAL, source TEXT, goal TEXT, songs TEXT)")
        con.execute("INSERT INTO history(ts,emotion) VALUES('2024-01-01','happy')"); con.commit(); con.close()
        os.environ["MOOD_DB"] = p
        try: database.init(); n = sqlite3.connect(p).execute("SELECT COUNT(*) FROM history").fetchone()[0]; self.assertEqual(n, 1)
        finally: os.environ["MOOD_DB"] = k

class Detection(unittest.TestCase):
    def setUp(self):
        self._o = (A.engine.available, A.engine._m, A.detect_face)
    def tearDown(self): A.engine.available, A.engine._m, A.detect_face = self._o
    def test_missing_model_503_no_prediction(self):
        model.MODEL_PATH = "/nonexistent.keras"; c = user("m1")
        r = c.post("/api/predict", data={"image": (frame(), "f.png")}); self.assertEqual(r.status_code, 503); self.assertNotIn("emotion", r.json)
        self.assertFalse(c.get("/api/model/status").json["model_available"])
        with self.assertRaises(model.ModelUnavailable): model.EmotionModel().predict(np.zeros((48, 48, 1), "float32"))
    def test_invalid_and_noface(self):
        A.engine.available = lambda: True; c = user("d1")
        self.assertEqual(c.post("/api/predict", data={"image": (io.BytesIO(b"junk"), "a.png")}).status_code, 400)
        self.assertEqual(c.post("/api/predict").status_code, 400)
        r = c.post("/api/predict", data={"image": (frame(), "a.png")}); self.assertEqual(r.status_code, 422); self.assertFalse(r.json["face_detected"])
    def test_class_mapping_and_flow(self):
        self.assertEqual(model.CLASSES, sorted(model.CLASSES)); self.assertEqual(len(model.CLASSES), 7)
        A.engine.available = lambda: True; A.engine._m = FakeKeras(); A.detect_face = lambda img: (np.zeros((48, 48, 1), "float32"), [0, 0, 48, 48])
        c = user("f1"); r = c.post("/api/predict", data={"image": (frame(), "a.png")}).json
        self.assertEqual(r["emotion"], "happy"); self.assertAlmostEqual(r["confidence"], 0.9)
        self.assertEqual(c.post("/api/recommendations", json={"emotion": "happy", "save": True}).status_code, 400)  # no token = no fake records
        rec = c.post("/api/recommendations", json={"token": r["token"], "save": True, "language": "Telugu"}).json
        self.assertTrue(rec["songs"] and all(s["language"] == "Telugu" for s in rec["songs"]))
        self.assertEqual(len(c.get("/api/history").json["history"]), 1)
        other = user("f2"); self.assertEqual(other.get("/api/history").json["history"], [])
        self.assertEqual(other.post("/api/recommendations", json={"token": r["token"]}).status_code, 400)  # token bound to user

class Music(unittest.TestCase):
    def test_languages_all_emotions(self):
        for lang in ["Telugu", "Hindi", "English"]:
            for e in recommender.EMOTIONS:
                for g in ["auto", "match", "relax", "energize", "uplift", "comfort"]:
                    for s in recommender.recommend(e, g, language=lang)["songs"]:
                        self.assertTrue(s["language"] == lang or (lang == "English" and s["language"] == "Instrumental"))
                self.assertTrue(recommender.recommend(e, language=lang)["songs"], (lang, e))
    def test_metadata_and_invalid(self):
        for s in recommender.CATALOGUE:
            for k in ("title", "artist", "language", "genre", "energy", "link", "source"): self.assertTrue(s[k], (s["id"], k))
            self.assertTrue(s["link"].startswith("https://"))
        for bad in [dict(emotion="x"), dict(emotion="happy", goal="zzz"), dict(emotion="happy", language="French")]:
            with self.assertRaises(ValueError): recommender.recommend(**bad)
        self.assertEqual(recommender.recommend("happy", genre="NoSuchGenre")["songs"], [])

if __name__ == "__main__": unittest.main()
