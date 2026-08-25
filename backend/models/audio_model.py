"""
Audio Deepfake Detector
Model: CNN on Log-Mel spectrograms — trained on ASVspoof2019-LA
Architecture: 4x Conv2D → GlobalAvgPool → Dense(128) → Dense(1, sigmoid)
Input: any audio file (mp3, wav, flac, ogg, m4a)
Output: prediction, confidence, processing_time
"""

import os
import io
import time
import logging
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_PATH    = Path(os.getenv("AUDIO_MODEL_PATH", "models/best_audio_model.keras"))
TARGET_SR     = 16_000
MAX_LEN       = 4 * TARGET_SR   # 4 seconds
MAX_PAD       = 128
N_MELS        = 64
INPUT_SHAPE   = (64, 128, 1)
FEATURE_DIM   = 128
FAKE_THRESHOLD = float(os.getenv("AUDIO_FAKE_THRESHOLD", "0.5"))

_model        = None
_MODEL_LOADED = False

SUPPORTED_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"}


# ── Model architecture (mirrors training notebook exactly) ────────────────────
def _build_model(tf):
    from tensorflow.keras import models, layers
    m = models.Sequential([
        layers.Input(shape=INPUT_SHAPE),
        layers.Conv2D(32,  (3,3), activation="relu", padding="same", name="conv1"),
        layers.MaxPooling2D((2,2)), layers.Dropout(0.25),
        layers.Conv2D(64,  (3,3), activation="relu", padding="same", name="conv2"),
        layers.MaxPooling2D((2,2)), layers.Dropout(0.25),
        layers.Conv2D(128, (3,3), activation="relu", padding="same", name="conv3"),
        layers.MaxPooling2D((2,2)), layers.Dropout(0.30),
        layers.Conv2D(128, (3,3), activation="relu", padding="same", name="conv4"),
        layers.GlobalAveragePooling2D(), layers.Dropout(0.30),
        layers.Dense(FEATURE_DIM, activation="relu", name="audio_feature_vector"),
        layers.Dropout(0.40),
        layers.Dense(1, activation="sigmoid", name="classifier_head"),
    ], name="AudioDeepfakeDetector")
    return m


def load_model():
    global _model, _MODEL_LOADED
    if _MODEL_LOADED:
        return _model

    import tensorflow as tf

    if MODEL_PATH.exists():
        logger.info(f"[AUDIO] Loading model from {MODEL_PATH}")
        try:
            _model = tf.keras.models.load_model(str(MODEL_PATH))
            logger.info("[AUDIO] Model loaded.")
        except Exception as e:
            logger.warning(f"[AUDIO] Load failed: {e}. Demo mode.")
            _model = _build_model(tf)
    else:
        logger.warning(f"[AUDIO] No model at {MODEL_PATH}. DEMO mode (random weights).")
        _model = _build_model(tf)

    _MODEL_LOADED = True
    return _model


# ── Feature extraction (identical to training notebook) ──────────────────────
def extract_logmel(audio: np.ndarray, sr: int = TARGET_SR) -> np.ndarray:
    import librosa
    mel    = librosa.feature.melspectrogram(
                 y=audio, sr=sr, n_fft=1024, hop_length=512, n_mels=N_MELS)
    log_mel = librosa.power_to_db(mel)
    log_mel = (log_mel - np.mean(log_mel)) / (np.std(log_mel) + 1e-6)
    if log_mel.shape[1] < MAX_PAD:
        log_mel = np.pad(log_mel, ((0,0), (0, MAX_PAD - log_mel.shape[1])))
    else:
        log_mel = log_mel[:, :MAX_PAD]
    return log_mel   # (64, 128)


def load_audio_bytes(file_bytes: bytes, original_ext: str = ".wav") -> np.ndarray:
    """
    Load audio from raw bytes using librosa.
    Writes to a temp file to handle formats librosa can't decode from a buffer.
    """
    import librosa

    ext = original_ext.lower() if original_ext.startswith(".") else f".{original_ext.lower()}"
    if ext not in SUPPORTED_EXTS:
        ext = ".wav"

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        audio, _ = librosa.load(tmp_path, sr=TARGET_SR, mono=True)
    finally:
        os.unlink(tmp_path)

    # Peak-normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    # Fixed length (4 s)
    if len(audio) > MAX_LEN:
        audio = audio[:MAX_LEN]
    else:
        audio = np.pad(audio, (0, MAX_LEN - len(audio)))

    return audio


def predict(file_bytes: bytes, filename: str = "audio.wav") -> dict:
    """Run deepfake detection on an audio file."""
    t0  = time.perf_counter()
    ext = Path(filename).suffix

    audio = load_audio_bytes(file_bytes, ext)
    logmel = extract_logmel(audio)

    # Shape: (1, 64, 128, 1)
    x = logmel[np.newaxis, :, :, np.newaxis].astype(np.float32)

    model = load_model()
    raw   = float(model.predict(x, verbose=0)[0][0])

    is_fake    = raw >= FAKE_THRESHOLD
    confidence = raw * 100 if is_fake else (1 - raw) * 100

    elapsed = time.perf_counter() - t0
    return {
        "prediction":      "Fake" if is_fake else "Real",
        "confidence":      round(confidence, 2),
        "processing_time": f"{elapsed:.2f}s",
        "model":           "CNN-LogMel (ASVspoof)",
        "raw_score":       round(raw, 4),
    }
