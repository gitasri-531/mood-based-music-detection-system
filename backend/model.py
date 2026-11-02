import os, numpy as np, cv2

CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]  # alphabetical = folder order
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(HERE, "models", "emotion_cnn.keras"))

class ModelUnavailable(Exception):
    pass

def build_model():
    from tensorflow import keras
    L = keras.layers
    m = keras.Sequential([
        L.Input((48, 48, 1)), L.Rescaling(1 / 255.0),  # normalisation lives inside the model
        L.Conv2D(32, 3, padding="same", activation="relu"), L.Conv2D(32, 3, padding="same", activation="relu"),
        L.MaxPooling2D(), L.Dropout(0.25),
        L.Conv2D(64, 3, padding="same", activation="relu"), L.Conv2D(64, 3, padding="same", activation="relu"),
        L.MaxPooling2D(), L.Dropout(0.25),
        L.Conv2D(128, 3, padding="same", activation="relu"), L.MaxPooling2D(), L.Dropout(0.25),
        L.Flatten(), L.Dense(256, activation="relu"), L.Dropout(0.5), L.Dense(len(CLASSES), activation="softmax")])
    m.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return m

_cascade = None
def detect_face(bgr):
    """Return (48x48x1 float32 face in 0-255, box) for the largest face, or (None, None)."""
    global _cascade
    if _cascade is None:
        _cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if _cascade.empty():
            _cascade = None
            raise RuntimeError("OpenCV face cascade could not be loaded (check opencv-python install).")
    if bgr is None or bgr.size == 0:
        return None, None
    gray = cv2.equalizeHist(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY))
    faces = _cascade.detectMultiScale(gray, 1.1, 5, minSize=(48, 48))
    if len(faces) == 0:
        return None, None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face = cv2.resize(gray[y:y + h, x:x + w], (48, 48)).astype("float32")
    return face[..., None], [int(x), int(y), int(w), int(h)]

class EmotionModel:
    def __init__(self):
        self._m = None
    def available(self):
        return os.path.exists(MODEL_PATH)
    def load(self):
        if self._m is None:
            if not self.available():
                raise ModelUnavailable("Trained model not found. Run train_model.py (see README).")
            try:
                from tensorflow import keras
            except ImportError:
                raise ModelUnavailable("TensorFlow is not installed.")
            self._m = keras.models.load_model(MODEL_PATH)
        return self._m
    def predict(self, face):
        p = self.load().predict(face[None], verbose=0)[0]
        return {c: float(v) for c, v in zip(CLASSES, p)}
