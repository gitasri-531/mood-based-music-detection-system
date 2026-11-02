"""Evaluate saved model on data/fer2013/test -> models/metrics.json (computed, never hard-coded)."""
import json, os, sys, numpy as np
from model import CLASSES, MODEL_PATH, HERE
test_dir = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "fer2013"), "test")
if not (os.path.isdir(test_dir) and os.path.exists(MODEL_PATH)):
    raise SystemExit("Need trained model and test directory.")
from tensorflow import keras
ds = keras.utils.image_dataset_from_directory(test_dir, color_mode="grayscale", image_size=(48, 48), batch_size=64,
                                              label_mode="int", class_names=CLASSES, shuffle=False)
y = np.concatenate([b for _, b in ds]); p = keras.models.load_model(MODEL_PATH).predict(ds).argmax(1)
n = len(CLASSES); cm = np.zeros((n, n), int)
for t, q in zip(y, p): cm[t, q] += 1
tp = np.diag(cm); prec = tp / np.maximum(cm.sum(0), 1); rec = tp / np.maximum(cm.sum(1), 1)
f1 = 2 * prec * rec / np.maximum(prec + rec, 1e-9)
out = {"accuracy": float(tp.sum() / cm.sum()), "macro_f1": float(f1.mean()), "classes": CLASSES,
       "per_class": {c: {"precision": float(prec[i]), "recall": float(rec[i]), "f1": float(f1[i]), "support": int(cm[i].sum())} for i, c in enumerate(CLASSES)},
       "confusion_matrix": cm.tolist()}
json.dump(out, open(os.path.join(HERE, "models", "metrics.json"), "w"), indent=2)
print(json.dumps(out["per_class"], indent=1), "\naccuracy", out["accuracy"], "macro_f1", out["macro_f1"])
