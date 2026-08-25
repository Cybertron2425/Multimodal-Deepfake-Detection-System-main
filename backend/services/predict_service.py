"""
services/predict_service.py

Orchestrates model inference.
Routes each media_type to its specialist runner and returns the
exact JSON shape the React frontend expects:
  { prediction, confidence, processing_time, model }
"""

import time
import logging
from typing import Literal

from services.model_registry import ModelRegistry
from services.runners.image_runner import ImageRunner
from services.runners.video_runner import VideoRunner
from services.runners.audio_runner import AudioRunner
from services.fusion_runner import FusionRunner


logger = logging.getLogger(__name__)

MediaType = Literal["image", "video", "audio"]

_RUNNER_MAP = {
    "image": ImageRunner,
    "video": FusionRunner,
    "audio": AudioRunner,
}


class PredictService:
    def __init__(self, config: dict):
        self.config   = config
        self.registry = ModelRegistry.get_instance()

    def predict(self, media_type: MediaType, file_path: str, original_filename: str) -> dict:
        """
        Run deepfake detection for the given media type.

        Returns:
            {
                "prediction":      "Fake" | "Real",
                "confidence":      float (0-100),
                "processing_time": "1.23s",
                "model":           str
            }
        Raises:
            RuntimeError on model inference failure.
        """
        runner_cls = _RUNNER_MAP.get(media_type)
        if not runner_cls:
            raise RuntimeError(f"No runner registered for media type '{media_type}'.")

        runner = runner_cls(registry=self.registry, config=self.config)

        t_start = time.perf_counter()
        try:
            result = runner.run(file_path=file_path, filename=original_filename)
            
        except Exception as exc:
            raise RuntimeError(f"Model inference failed: {exc}") from exc
        elapsed = time.perf_counter() - t_start
            # Always override processing_time with end-to-end wall time
        result["processing_time"] = f"{elapsed:.2f}s"
        return result
