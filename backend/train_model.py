"""Usage: python train_model.py --data data/fer2013 [--epochs 30]
Expects data/fer2013/train/<emotion>/*.png and data/fer2013/test/<emotion>/*.png (Kaggle msambare/fer2013).
CSV version is not supported."""
import argparse, json, os
from model import CLASSES, MODEL_PATH, HERE, build_model

ap = argparse.ArgumentParser()
ap.add_argument("--data", default=os.path.join(HERE, "data", "fer2013"))
ap.add_argument("--epochs", type=int, default=30)
ap.add_argument("--batch", type=int, default=64)
a = ap.parse_args()
train_dir = os.path.join(a.data, "train")
if not os.path.isdir(train_dir):
    raise SystemExit(f"Dataset not found at {train_dir}. See backend/data/README.md")
import tensorflow as tf
from tensorflow import keras
keras.utils.set_random_seed(42)
kw = dict(color_mode="grayscale", image_size=(48, 48), batch_size=a.batch, label_mode="int", class_names=CLASSES)
tr = keras.utils.image_dataset_from_directory(train_dir, validation_split=0.15, subset="training", seed=42, **kw)
va = keras.utils.image_dataset_from_directory(train_dir, validation_split=0.15, subset="validation", seed=42, **kw)
aug = keras.Sequential([keras.layers.RandomFlip("horizontal"), keras.layers.RandomRotation(0.08), keras.layers.RandomZoom(0.1)])
tr = tr.map(lambda x, y: (aug(x, training=True), y)).prefetch(tf.data.AUTOTUNE)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
cb = [keras.callbacks.EarlyStopping(patience=6, restore_best_weights=True, monitor="val_accuracy"),
      keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor="val_accuracy")]
h = build_model().fit(tr, validation_data=va, epochs=a.epochs, callbacks=cb)
json.dump({k: [float(v) for v in vs] for k, vs in h.history.items()}, open(os.path.join(HERE, "models", "history.json"), "w"))
print("Saved", MODEL_PATH, "- now run: python evaluate_model.py")
