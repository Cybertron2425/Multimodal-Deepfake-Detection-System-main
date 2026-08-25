"""
services/runners/audio_runner.py

CNN + Log-Mel spectrogram audio deepfake detection.
Feature extraction mirrors image_model.py (which is actually the AUDIO notebook):
  TARGET_SR = 16000
  MAX_LEN   = 4 * 16000  (4 seconds)
  N_MELS    = 64
  MAX_PAD   = 128
  Input shape: (1, 64, 128, 1)
"""

import os
import logging
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_NAME  = "CNN-LogMel (ASVspoof)"
TARGET_SR   = 16_000
MAX_LEN     = 4 * TARGET_SR   # 4 seconds
N_MELS      = 64
MAX_PAD     = 128
INPUT_SHAPE = (64, 128, 1)

# Audio formats supported (matches frontend ACCEPTED_FILES audio/*)
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}


class AudioRunner:
    def __init__(self, registry, config: dict):
        self.registry  = registry
        self.config    = config
        self.threshold = float(config.get("AUDIO_FAKE_THRESHOLD", 0.5))

    def run(self, file_path: str, filename: str) -> dict:
        model  = self.registry.get_audio_model(self.config)

        audio  = self._load_audio(file_path, filename)
        logmel = self._extract_logmel(audio)

        # Shape: (1, 64, 128, 1)
        x   = logmel[np.newaxis, :, :, np.newaxis].astype(np.float32)
        raw = float(model.predict(x, verbose=0)[0][0])
        logger.info(f"RAW AUDIO SCORE = {raw}")

        return self._format(raw)

    # ── Audio loading (identical to notebook) ─────────────────────────────────
    def _load_audio(self, file_path: str, filename: str) -> np.ndarray:
        """
        Load audio → resample to 16 kHz mono → peak-normalize → fixed 4-second clip.
        This is verbatim from the load_and_extract() function in the notebook.
        """
        import librosa

        audio, _ = librosa.load(file_path, sr=TARGET_SR, mono=True)

        # Peak-normalize (as in notebook)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))

        # Fixed-length clip
        if len(audio) > MAX_LEN:
            audio = audio[:MAX_LEN]
        else:
            audio = np.pad(audio, (0, MAX_LEN - len(audio)))

        return audio

    # ── Feature extraction (identical to notebook extract_logmel()) ───────────
    def _extract_logmel(self, audio: np.ndarray) -> np.ndarray:
        """
        Verbatim copy of extract_logmel() from the training notebook.
        Returns array of shape (64, 128).
        """
        import librosa

        mel     = librosa.feature.melspectrogram(
                      y=audio, sr=TARGET_SR,
                      n_fft=1024, hop_length=512, n_mels=N_MELS)
        log_mel = librosa.power_to_db(mel)
        log_mel = (log_mel - np.mean(log_mel)) / (np.std(log_mel) + 1e-6)

        if log_mel.shape[1] < MAX_PAD:
            log_mel = np.pad(log_mel, ((0, 0), (0, MAX_PAD - log_mel.shape[1])))
        else:
            log_mel = log_mel[:, :MAX_PAD]

        return log_mel   # (64, 128)

    def _format(self, raw: float) -> dict:
        is_fake    = raw >= self.threshold
        confidence = raw * 100 if is_fake else (1 - raw) * 100
        
        return{
                "prediction": "Fake" if is_fake else "Real",
                "confidence": round(confidence, 2),
                "model": MODEL_NAME,
                "raw_score": round(raw, 4),

                "audio_score": float(raw),
                "audio_confidence": float(confidence / 100),
        }
        