"""
Image Deepfake Detector
Model: EfficientNet-B4 fine-tuned on CIFAKE / 140k Real-Fake dataset
Input: any image file → resized to 224x224
Output: prediction (Real/Fake), confidence %
"""

import os
import time
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Lazy imports so server starts even if GPU libs are absent ──────────────────
_tf = None
_model = None
_MODEL_LOADED = False

MODEL_PATH = Path(os.getenv("IMAGE_MODEL_PATH", "models/best_image_model.keras"))

INPUT_SHAPE = (224, 224)
FAKE_THRESHOLD = 0.5


def _load_tf():
    global _tf
    if _tf is None:
        import tensorflow as tf
        _tf = tf
    return _tf


def _build_efficientnet(tf):
    """Build EfficientNet-B4 architecture matching training code."""
    base = tf.keras.applications.EfficientNetB4(
        include_top=False,
        weights=None,
        input_shape=(*INPUT_SHAPE, 3),
        pooling="avg",
    )
    inputs = tf.keras.Input(shape=(*INPUT_SHAPE, 3))
    x = base(inputs, training=False)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    return tf.keras.Model(inputs, outputs, name="EfficientNetB4_Deepfake")


def load_model():
    """Load weights if saved model exists, otherwise build fresh (demo mode)."""
    global _model, _MODEL_LOADED
    if _MODEL_LOADED:
        return _model

    tf = _load_tf()
    if MODEL_PATH.exists():
        logger.info(f"[IMAGE] Loading model from {MODEL_PATH}")
        try:
            _model = tf.keras.models.load_model(str(MODEL_PATH))
            logger.info("[IMAGE] Model loaded successfully.")
        except Exception as e:
            logger.warning(f"[IMAGE] Failed to load saved model: {e}. Using random weights (demo mode).")
            _model = _build_efficientnet(tf)
    else:
        logger.warning(f"[IMAGE] No model file at {MODEL_PATH}. Running in DEMO mode (random weights).")
        _model = _build_efficientnet(tf)

    _MODEL_LOADED = True
    return _model


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """Decode bytes → PIL → normalize → numpy array (1, 224, 224, 3)."""
    tf = _load_tf()
    from PIL import Image
    import io

    img = Image.open(io.BytesIO(file_bytes)).convert("RGB").resize(INPUT_SHAPE)
    arr = np.array(img, dtype=np.float32) / 255.0
    # EfficientNet expects values in [0,1]; apply per-channel ImageNet norm
    mean = np.array([0.485, 0.456, 0.406])
    std  = np.array([0.229, 0.224, 0.225])
    arr  = (arr - mean) / std
    return np.expand_dims(arr, 0).astype(np.float32)


def predict(file_bytes: bytes) -> dict:
    """
    Run deepfake detection on an image.
    Returns dict: prediction, confidence, processing_time, model
    """
    t0 = time.perf_counter()

    model = load_model()
    x = preprocess_image(file_bytes)
    raw = float(model.predict(x, verbose=0)[0][0])

    is_fake = raw >= FAKE_THRESHOLD
    confidence = raw * 100 if is_fake else (1 - raw) * 100

    elapsed = time.perf_counter() - t0

    return {
        "prediction":      "Fake" if is_fake else "Real",
        "confidence":      round(confidence, 2),
        "processing_time": f"{elapsed:.2f}s",
        "model":           "EfficientNet-B4",
        "raw_score":       round(raw, 4),
    }
