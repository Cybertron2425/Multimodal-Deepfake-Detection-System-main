# backend/services/runners/audio_runner.py

import logging
import os

import librosa
import numpy as np


logger = logging.getLogger(__name__)


class AudioRunner:
    """
    Audio deepfake detection runner.

    Supports:
        MP3, WAV, FLAC, OGG, M4A

    Pipeline:
        Audio
          ↓
        16 kHz Mono
          ↓
        4-second windows
          ↓
        Log-Mel Spectrogram
          ↓
        CNN
          ↓
        Aggregated prediction
    """

    TARGET_SR = 16000

    # Must match the model/training preprocessing.
    DURATION = 4.0
    N_MELS = 64
    N_FFT = 1024
    HOP_LENGTH = 256
    TARGET_FRAMES = 128

    # Window overlap.
    WINDOW_HOP = 2.0

    def __init__(self, registry, config):
        self.registry = registry
        self.config = config

    def run(self, file_path: str, filename: str) -> dict:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Audio file not found: {file_path}"
            )

        logger.info(
            "[AUDIO] Processing: %s",
            filename
        )

        # ---------------------------------------------------------
        # Load audio
        # ---------------------------------------------------------

        audio, sr = librosa.load(
            file_path,
            sr=self.TARGET_SR,
            mono=True
        )

        if audio is None or len(audio) == 0:
            raise ValueError("Could not decode audio file.")

        audio = audio.astype(np.float32)

        logger.info(
            "[AUDIO] Loaded audio: %.2f sec | SR=%d",
            len(audio) / self.TARGET_SR,
            self.TARGET_SR
        )

        # ---------------------------------------------------------
        # Remove DC offset
        # ---------------------------------------------------------

        audio = audio - np.mean(audio)

        # ---------------------------------------------------------
        # Peak normalization
        # ---------------------------------------------------------

        peak = np.max(np.abs(audio))

        if peak > 1e-8:
            audio = audio / peak

        # ---------------------------------------------------------
        # Create overlapping windows
        # ---------------------------------------------------------

        window_samples = int(
            self.DURATION * self.TARGET_SR
        )

        hop_samples = int(
            self.WINDOW_HOP * self.TARGET_SR
        )

        audio_length = len(audio)

        windows = []

        if audio_length <= window_samples:

            padded = np.pad(
                audio,
                (0, window_samples - audio_length),
                mode="constant"
            )

            windows.append(padded)

        else:

            start = 0

            while start + window_samples <= audio_length:

                window = audio[
                    start:start + window_samples
                ]

                windows.append(window)

                start += hop_samples

            # Include final part of the audio if not already included.
            if start < audio_length:

                final_window = audio[-window_samples:]

                windows.append(final_window)

        logger.info(
            "[AUDIO] Number of analysis windows: %d",
            len(windows)
        )

        # ---------------------------------------------------------
        # Get trained audio model
        # ---------------------------------------------------------

        model = self.registry.get_audio_model(
            self.config
        )

        if model is None:
            raise RuntimeError(
                "Audio model could not be loaded."
            )

        # ---------------------------------------------------------
        # Predict every window
        # ---------------------------------------------------------

        window_scores = []

        for index, window in enumerate(windows):

            try:

                spectrogram = self._make_logmel(
                    window
                )

                prediction = model.predict(
                    spectrogram,
                    verbose=0
                )

                score = float(
                    np.asarray(prediction).reshape(-1)[0]
                )

                score = float(
                    np.clip(score, 0.0, 1.0)
                )

                window_scores.append(score)

                logger.info(
                    "[AUDIO] Window %d/%d score=%.4f",
                    index + 1,
                    len(windows),
                    score
                )

            except Exception as exc:

                logger.warning(
                    "[AUDIO] Window %d failed: %s",
                    index + 1,
                    exc
                )

        if not window_scores:
            raise RuntimeError(
                "Audio model failed on all analysis windows."
            )

        scores = np.asarray(
            window_scores,
            dtype=np.float32
        )

        # ---------------------------------------------------------
        # Robust aggregation
        # ---------------------------------------------------------

        mean_score = float(
            np.mean(scores)
        )

        median_score = float(
            np.median(scores)
        )

        # Combine mean + median.
        #
        # Median reduces the influence of one unusual window,
        # while mean keeps information from all windows.
        final_score = (
            0.6 * mean_score
            + 0.4 * median_score
        )

        final_score = float(
            np.clip(final_score, 0.0, 1.0)
        )

        # ---------------------------------------------------------
        # Final prediction
        # ---------------------------------------------------------

        prediction = (
            "Fake"
            if final_score >= 0.5
            else "Real"
        )

        confidence = (
            final_score * 100.0
            if prediction == "Fake"
            else (1.0 - final_score) * 100.0
        )

        logger.info(
            "[AUDIO] Final score=%.4f | prediction=%s | confidence=%.2f%%",
            final_score,
            prediction,
            confidence
        )

        # ---------------------------------------------------------
        # Return existing API-compatible structure
        # ---------------------------------------------------------

        return {
            "prediction": prediction,
            "confidence": round(confidence, 2),

            "model": "Audio CNN - Log-Mel Spectrogram",

            "raw_score": round(
                final_score,
                4
            ),

            "audio_score": round(
                final_score,
                4
            ),

            "window_scores": [
                round(float(score), 4)
                for score in window_scores
            ],

            "num_windows": len(
                window_scores
            ),

            "mean_score": round(
                mean_score,
                4
            ),

            "median_score": round(
                median_score,
                4
            ),
        }

    # =============================================================
    # Log-Mel Spectrogram
    # =============================================================

    def _make_logmel(self, audio):

        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=self.TARGET_SR,
            n_fft=self.N_FFT,
            hop_length=self.HOP_LENGTH,
            n_mels=self.N_MELS,
            power=2.0
        )

        log_mel = librosa.power_to_db(
            mel,
            ref=np.max
        )

        # ---------------------------------------------------------
        # Force exactly 128 time frames
        # ---------------------------------------------------------

        if log_mel.shape[1] < self.TARGET_FRAMES:

            pad_width = (
                self.TARGET_FRAMES
                - log_mel.shape[1]
            )

            log_mel = np.pad(
                log_mel,
                (
                    (0, 0),
                    (0, pad_width)
                ),
                mode="constant",
                constant_values=log_mel.min()
            )

        elif log_mel.shape[1] > self.TARGET_FRAMES:

            log_mel = log_mel[
                :,
                :self.TARGET_FRAMES
            ]

        # ---------------------------------------------------------
        # Add CNN dimensions
        #
        # Final shape:
        # (batch, 64, 128, 1)
        # ---------------------------------------------------------

        log_mel = log_mel.astype(
            np.float32
        )

        log_mel = np.expand_dims(
            log_mel,
            axis=-1
        )

        log_mel = np.expand_dims(
            log_mel,
            axis=0
        )

        return log_mel