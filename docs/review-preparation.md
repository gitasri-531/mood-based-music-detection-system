# Viva preparation (short)
**60-second intro:** The app reads a face from the webcam, crops it with OpenCV, and a CNN trained on FER-2013 predicts one of 7 expressions. A rule-based engine maps expression + listening goal to songs from a local catalogue. History is stored in SQLite and charted with Recharts.

**Implementation (2 min):** React captures a frame -> Flask `/api/predict` -> Haar cascade -> 48x48 gray -> CNN softmax -> UI smooths last 5 predictions -> `/api/recommendations` scores songs by tag overlap -> optional save to SQLite -> analytics.

**Key concepts:** Convolution = learnable filters detecting local patterns (edges -> parts of face). ReLU = max(0,x), adds non-linearity. Max-pooling = downsampling, gives small translation invariance. Dropout = randomly disables neurons to reduce overfitting. Softmax = turns scores into probabilities summing to 1. Cross-entropy = penalises low probability on the true class. Adam = adaptive-learning-rate gradient optimiser.
**Why CNN:** shares weights across space, far fewer parameters than dense nets on images. **Why FER-2013:** free, standard benchmark, 7 classes, 48x48 so trains on a laptop.
**Metrics:** accuracy = overall correct; precision = correct among predicted-positive; recall = found among actual-positive; F1 = harmonic mean; macro-F1 = mean over classes (important because classes are imbalanced); confusion matrix shows which classes get mixed up.
**Splits:** train fits weights, validation tunes/early-stops, test gives the final unbiased estimate.
**Limits/ethics:** expressions != emotions, dataset bias, noisy labels; images not stored, processed locally, consent via browser permission. **Future:** transfer learning, official music APIs, better face detector.
