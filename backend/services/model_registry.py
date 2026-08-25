"""
services/model_registry.py

Singleton that holds all three AI models in memory.
Models are loaded once at first access (lazy) and reused across all requests.
Thread-safe via a simple lock.
"""

import logging
import threading
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ImageFusionPipeline:
    feature_extractor: object
    svm_model: object
    deep_scaler: object
    land_scaler: object
    pca: object
    landmark_predictor: object


class ModelRegistry:
    """
    Holds references to all three AI models.
    Use ModelRegistry.get_instance() — never instantiate directly.
    """

    _instance: Optional["ModelRegistry"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._image_model         = None
        self._image_fusion_pipeline = None
        self._video_model         = None
        self._audio_model         = None
        self._config              = {}

        self.image_loaded         = False
        self.image_fusion_loaded  = False
        self.video_loaded         = False
        self.audio_loaded         = False

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ── Image model ───────────────────────────────────────────────────────────
    def get_image_model(self, config: dict):
        if self._image_model is None:
            with self._lock:
                if self._image_model is None:
                    self._image_model = self._load_image_model(config)
        return self._image_model

    def get_image_fusion_pipeline(self, config: dict):
        if self._image_fusion_pipeline is None:
            with self._lock:
                if self._image_fusion_pipeline is None:
                    self._image_fusion_pipeline = self._load_image_fusion_pipeline(config)
        return self._image_fusion_pipeline

    def _load_image_model(self, config: dict):
        print("LOADING IMAGE MODEL...")
        import tensorflow as tf
        print("TF IMPORT SUCCESS")
        from pathlib import Path

        model_path = config.get("IMAGE_MODEL_PATH", "")
        logger.info(f"[IMAGE] Loading model from: {model_path}")

        if Path(model_path).exists():
            try:
                model = tf.keras.models.load_model(model_path)
                self.image_loaded = True
                logger.info("[IMAGE] Weights loaded successfully.")
                return model
            except Exception as exc:
                logger.warning(f"[IMAGE] Could not load saved weights: {exc}. Using demo mode.")

        # Demo mode — build architecture, random weights (no .keras file needed)
        model = self._build_efficientnet(tf, config)
        self.image_loaded = True
        logger.warning("[IMAGE] Running in DEMO mode (no weight file found).")
        return model

    def _load_image_fusion_pipeline(self, config: dict):
        try:
            import joblib
            import timm
            import torch
            import dlib
            from pathlib import Path
        except ImportError as err:
            logger.warning(f"[IMAGE-FUSION] Dependencies missing ({err}). Fusion pipeline disabled.")
            return None

        svm_path      = config.get("IMAGE_FUSION_SVM_PATH", "")
        pca_path      = config.get("IMAGE_FUSION_PCA_PATH", "")
        deep_path     = config.get("IMAGE_FUSION_DEEP_SCALER_PATH", "")
        land_path     = config.get("IMAGE_FUSION_LAND_SCALER_PATH", "")
        landmark_path = config.get("IMAGE_FUSION_LANDMARK_PATH", "")

        logger.info("[IMAGE-FUSION] Attempting to load fusion artifacts.")

        if not all(Path(p).exists() for p in [svm_path, pca_path, deep_path, land_path, landmark_path]):
            logger.warning("[IMAGE-FUSION] One or more fusion artifacts are missing. Fusion disabled.")
            return None

        try:
            svm_model      = joblib.load(svm_path)
            pca            = joblib.load(pca_path)
            deep_scaler    = joblib.load(deep_path)
            land_scaler    = joblib.load(land_path)
            landmark_predictor = dlib.shape_predictor(landmark_path)

            feature_extractor = timm.create_model(
                "efficientnet_b4",
                pretrained=True,
                num_classes=0,
            )
            feature_extractor.eval()

            pipeline = ImageFusionPipeline(
                feature_extractor=feature_extractor,
                svm_model=svm_model,
                deep_scaler=deep_scaler,
                land_scaler=land_scaler,
                pca=pca,
                landmark_predictor=landmark_predictor,
            )

            self.image_fusion_loaded = True
            logger.info("[IMAGE-FUSION] Fusion pipeline loaded successfully.")
            return pipeline
        except Exception as exc:
            logger.warning(f"[IMAGE-FUSION] Failed to load fusion pipeline: {exc}. Fusion disabled.")
            return None

    @staticmethod
    def _build_efficientnet(tf, config):
        input_shape = (224, 224, 3)
        base = tf.keras.applications.EfficientNetB4(
            include_top=False, weights=None,
            input_shape=input_shape, pooling="avg",
        )
        inputs = tf.keras.Input(shape=input_shape)
        x = base(inputs, training=False)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(256, activation="relu")(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
        return tf.keras.Model(inputs, outputs, name="EfficientNetB4_Deepfake")

    # ── Video model ───────────────────────────────────────────────────────────
    def get_video_model(self, config: dict):
        if self._video_model is None:
            with self._lock:
                if self._video_model is None:
                    self._video_model = self._load_video_model(config)
        return self._video_model

    def _load_video_model(self, config: dict):
        import torch
        import torch.nn as nn
        from torchvision import models
        from pathlib import Path

        model_path = config.get("VIDEO_MODEL_PATH", "")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"[VIDEO] Loading model from: {model_path} | device={device}")

        # Build ResNeXt-101 architecture matching training notebook
        net = models.resnext101_32x8d(weights=None)
        net.fc = nn.Linear(
            net.fc.in_features,
            2
        )
        if Path(model_path).exists():
            try:
                state = torch.load(model_path, map_location=device)
                net.load_state_dict(state)
                logger.info("[VIDEO] Weights loaded successfully.")
                self.video_loaded = True
            except Exception as exc:
                logger.warning(f"[VIDEO] Could not load weights: {exc}. Demo mode.")
                self.video_loaded = True
        else:
            logger.warning("[VIDEO] No weight file found. Demo mode.")
            self.video_loaded = True

        net.to(device).eval()
        return net

    # ── Audio model ───────────────────────────────────────────────────────────
    def get_audio_model(self, config: dict):
        if self._audio_model is None:
            with self._lock:
                if self._audio_model is None:
                    self._audio_model = self._load_audio_model(config)
        return self._audio_model

    def _load_audio_model(self, config: dict):
        print("LOADING AUDIO MODEL...")
        import tensorflow as tf
        print("TF IMPORT SUCCESS AUDIO")
        from pathlib import Path

        model_path = config.get("AUDIO_MODEL_PATH", "")
        logger.info(f"[AUDIO] Loading model from: {model_path}")

        if Path(model_path).exists():
            try:
                model = tf.keras.models.load_model(model_path)
                self.audio_loaded = True
                logger.info("[AUDIO] Weights loaded successfully.")
                return model
            except Exception as exc:
                logger.warning(f"[AUDIO] Could not load model: {exc}. Demo mode.")

        # Demo mode — build architecture from training notebook
        model = self._build_audio_cnn(tf)
        self.audio_loaded = True
        logger.warning("[AUDIO] Running in DEMO mode (no weight file found).")
        return model

    @staticmethod
    def _build_audio_cnn(tf):
        """Exact architecture from image_model.py (audio CNN) notebook."""
        from tensorflow.keras import models as km, layers
        INPUT_SHAPE  = (64, 128, 1)
        FEATURE_DIM  = 128
        m = km.Sequential([
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
