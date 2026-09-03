"""
services/runners/video_runner.py

Fine-tuned SigLIP V2 video deepfake detector.

Pipeline:
    Video
      ↓
    16 uniformly sampled frames
      ↓
    Fine-tuned SigLIP V2
      ↓
    Frame-level Fake / Real probabilities
      ↓
    Average Fake probability
      ↓
    Final REAL / FAKE prediction
"""

import logging

import cv2
import numpy as np
from PIL import Image


logger = logging.getLogger(__name__)

MODEL_NAME = "Fine-tuned SigLIP V2 Deepfake Detector"


class VideoRunner:

    def __init__(self, registry, config):

        self.registry = registry
        self.config = config

        self.frame_count = int(
            config.get(
                "VIDEO_FRAME_COUNT",
                16
            )
        )

        self.fake_thresh = float(
            config.get(
                "VIDEO_FAKE_THRESHOLD",
                0.50
            )
        )
        self._last_frame_metadata = []

    # =========================================================
    # MAIN VIDEO PREDICTION
    # =========================================================

    def run(
        self,
        file_path: str,
        filename: str
    ) -> dict:

        import torch

        # -----------------------------------------------------
        # Load fine-tuned V2 model
        # -----------------------------------------------------

        model, processor, device = (
            self.registry.get_video_model_v2(
                self.config
            )
        )

        logger.info(
            f"[VIDEO-V2] Processing: {filename}"
        )

        logger.info(
            f"[VIDEO-V2] Device: {device}"
        )

        # -----------------------------------------------------
        # Extract frames
        # -----------------------------------------------------

        frames = self._extract_frames(
            file_path
        )

        if not frames:

            logger.warning(
                "[VIDEO-V2] No frames extracted."
            )

            return {
                "prediction": "Real",
                "confidence": 50.0,
                "model": MODEL_NAME,
                "raw_score": 0.0,
                "video_score": 0.0,
                "video_confidence": 0.50,
                "fake_ratio": 0.0,
                "frame_probs": [],
                "frame_evidence": [],
                "frames_analyzed": 0,
                "frames": [],
            }

        fake_probs = []
        real_probs = []
        frame_evidence = []

        # -----------------------------------------------------
        # Predict each frame
        # -----------------------------------------------------

        with torch.no_grad():

            for frame_no, frame in enumerate(
                frames,
                start=1
            ):

                try:

                    inputs = processor(
                        images=frame,
                        return_tensors="pt"
                    )

                    inputs = {
                        key: value.to(device)
                        for key, value in inputs.items()
                    }

                    outputs = model(
                        **inputs
                    )

                    probabilities = torch.softmax(
                        outputs.logits,
                        dim=1
                    )[0]

                    # Model mapping:
                    # 0 = Fake
                    # 1 = Real

                    fake_probability = float(
                        probabilities[0].item()
                    )

                    real_probability = float(
                        probabilities[1].item()
                    )

                    fake_probs.append(
                        fake_probability
                    )

                    real_probs.append(
                        real_probability
                    )

                    frame_prediction = (
                        "FAKE"
                        if fake_probability > real_probability
                        else "REAL"
                    )

                    metadata = self._last_frame_metadata[frame_no - 1]
                    frame_evidence.append({
                        "frame_number": frame_no,
                        "frame_index": metadata["frame_index"],
                        "timestamp_seconds": metadata["timestamp_seconds"],
                        "fake_probability": round(fake_probability * 100.0, 2),
                        "prediction": frame_prediction,
                    })

                    logger.info(
                        "[VIDEO-V2] Frame %02d | "
                        "%s | Fake: %.2f%% | Real: %.2f%%",
                        frame_no,
                        frame_prediction,
                        fake_probability * 100,
                        real_probability * 100,
                    )

                except Exception as exc:

                    logger.warning(
                        "[VIDEO-V2] Frame %02d failed: %s",
                        frame_no,
                        exc,
                    )

        # -----------------------------------------------------
        # No successful frames
        # -----------------------------------------------------

        if not fake_probs:

            return {
                "prediction": "Real",
                "confidence": 50.0,
                "model": MODEL_NAME,
                "raw_score": 0.0,
                "video_score": 0.0,
                "video_confidence": 0.50,
                "fake_ratio": 0.0,
                "frame_probs": [],
                "frame_evidence": [],
                "frames_analyzed": 0,
                "frames": [],
            }

        # -----------------------------------------------------
        # Aggregate probabilities
        # -----------------------------------------------------

        fake_probs_array = np.asarray(
            fake_probs,
            dtype=np.float32
        )

        real_probs_array = np.asarray(
            real_probs,
            dtype=np.float32
        )

        average_fake = float(
            np.mean(fake_probs_array)
        )

        average_real = float(
            np.mean(real_probs_array)
        )

        # Percentage of frames where
        # Fake probability is > 50%

        fake_frame_ratio = float(
            np.mean(
                fake_probs_array > 0.50
            )
        )

        # -----------------------------------------------------
        # Final decision
        # -----------------------------------------------------

        if average_fake >= self.fake_thresh:

            prediction = "Fake"

            confidence = (
                average_fake * 100.0
            )

        else:

            prediction = "Real"

            confidence = (
                average_real * 100.0
            )

        # -----------------------------------------------------
        # Final logs
        # -----------------------------------------------------

        logger.info(
            "[VIDEO-V2] Total successful frames: %d",
            len(fake_probs)
        )

        logger.info(
            "[VIDEO-V2] Average Fake Probability: %.4f",
            average_fake
        )

        logger.info(
            "[VIDEO-V2] Average Real Probability: %.4f",
            average_real
        )

        logger.info(
            "[VIDEO-V2] Fake Frame Ratio: %.4f",
            fake_frame_ratio
        )

        logger.info(
            "[VIDEO-V2] FINAL PREDICTION: %s",
            prediction
        )

        logger.info(
            "[VIDEO-V2] FINAL CONFIDENCE: %.2f%%",
            confidence
        )

        # -----------------------------------------------------
        # Return result
        # -----------------------------------------------------

        return {
            "prediction": prediction,

            "confidence": round(
                confidence,
                2
            ),

            "model": MODEL_NAME,

            "raw_score": round(
                average_fake,
                6
            ),

            "video_score": round(
                average_fake,
                6
            ),

            "video_confidence": round(
                confidence / 100.0,
                6
            ),

            "fake_ratio": round(
                fake_frame_ratio,
                6
            ),

            "frame_probs": [
                round(
                    float(probability),
                    6
                )
                for probability in fake_probs
            ],

            # JSON-safe per-frame evidence for the frontend report.
            "frame_evidence": frame_evidence,

            "frames_analyzed": len(
                fake_probs
            ),

            # Required internally by multimodal fusion.
            "frames": frames,
        }

    # =========================================================
    # FRAME EXTRACTION
    # =========================================================

    def _extract_frames(
        self,
        video_path: str
    ):

        cap = cv2.VideoCapture(
            video_path
        )

        if not cap.isOpened():

            logger.error(
                "[VIDEO-V2] Could not open video: %s",
                video_path
            )

            return []

        total_frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        if total_frames <= 0:

            cap.release()

            logger.error(
                "[VIDEO-V2] Video contains no frames."
            )

            return []

        sample_count = min(
            self.frame_count,
            total_frames
        )

        indices = np.linspace(
            0,
            total_frames - 1,
            sample_count,
            dtype=int
        )

        logger.info(
            "[VIDEO-V2] Total frames: %d",
            total_frames
        )

        logger.info(
            "[VIDEO-V2] Selected frame indices: %s",
            indices.tolist()
        )

        frames = []
        self._last_frame_metadata = []
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)

        for index in indices:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(index)
            )

            success, frame = cap.read()

            if not success:

                logger.warning(
                    "[VIDEO-V2] Failed to read frame index %d",
                    index
                )

                continue

            # OpenCV BGR → RGB

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(
                frame_rgb
            )

            frames.append(
                image
            )
            self._last_frame_metadata.append({
                "frame_index": int(index),
                "timestamp_seconds": round(float(index) / fps, 3) if fps > 0 else None,
            })

        cap.release()

        logger.info(
            "[VIDEO-V2] Successfully extracted %d/%d frames",
            len(frames),
            sample_count
        )

        return frames
