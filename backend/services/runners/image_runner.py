"""
services/runners/image_runner.py

EfficientNet-B4 image deepfake detection.
Preprocessing matches the training pipeline from image_model.py (notebook):
  - Resize to 224×224
  - Normalize to [0, 1]
  - Apply ImageNet channel-wise mean/std
"""


#from curses import raw
import logging
import os
from pyexpat import features
import tempfile
import tempfile
import numpy as np
from sklearn import pipeline

logger = logging.getLogger(__name__)

# ImageNet normalization constants
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

INPUT_SIZE        = (224, 224)
FUSION_INPUT_SIZE = (380, 380)
MODEL_NAME        = "EfficientNet-B4"
FUSION_MODEL_NAME = "EfficientNet-B4 + Dlib + SVM Fusion"

FACIAL_REGIONS = {
    "jaw":       list(range(0, 17)),
    "nose":      list(range(27, 36)),
    "left_eye":  list(range(42, 48)),
    "right_eye": list(range(36, 42)),
    "mouth":     list(range(48, 68)),
}


class ImageRunner:
    def __init__(self, registry, config: dict):
        self.registry  = registry
        self.config    = config
        self.threshold = float(config.get("IMAGE_FAKE_THRESHOLD", 0.5))

    def run(self, file_path: str, filename: str) -> dict:
        pipeline = self.registry.get_image_fusion_pipeline(self.config)
        if pipeline is not None:
            try:
                return self._run_fusion(file_path, pipeline)
            except Exception as exc:
                logger.warning(f"[IMAGE-FUSION] Fusion inference failed: {exc}. Falling back to standard model.")

        model = self.registry.get_image_model(self.config)
        x     = self._preprocess(file_path)

        raw = float(model.predict(x, verbose=0)[0][0])
        return self._format(raw)
    
    def predict_pil(self, pil_image):
       
        pipeline = self.registry.get_image_fusion_pipeline(self.config)
        if pipeline is not None:
            try:
                return self._predict_pil_fusion(
                    pil_image,
                    pipeline
               )
            except Exception as exc:
                logger.warning(
                    f"[IMAGE-FUSION] {exc}"
                )
        model = self.registry.get_image_model(self.config)
                
        img = pil_image.resize(INPUT_SIZE)
                
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - _MEAN) / _STD
        arr = np.expand_dims(arr, 0)
        raw = float(
            model.predict(
                arr,
                verbose=0
            )[0][0]
        )
        return raw
    
    def _predict_pil_fusion(self, pil_image, pipeline):

        import tempfile

        tmp = tempfile.NamedTemporaryFile(
           suffix=".jpg",
           delete=False
        )
        
        tmp.close()

        pil_image.save(tmp.name)

        result = self._run_fusion(
            tmp.name,
            pipeline
        )

        os.remove(tmp.name)

        return result["image_score"]

    def _run_fusion(self, path: str, pipeline) -> dict:
        deep_feats = self._extract_deep_features(path, pipeline.feature_extractor)
        land_feats = self._extract_landmark_features(path, pipeline.landmark_predictor)

        if deep_feats is None or land_feats is None:
            raise RuntimeError("Failed to extract fusion features from image.")

        deep_scaled  = pipeline.deep_scaler.transform(deep_feats.reshape(1, -1))
        land_scaled  = pipeline.land_scaler.transform(land_feats.reshape(1, -1))
        combined     = np.hstack([deep_scaled, land_scaled])
        combined_pca = pipeline.pca.transform(combined)

        pred = int(pipeline.svm_model.predict(combined_pca)[0])
        raw  = float(pipeline.svm_model.decision_function(combined_pca)[0])

        prob_fake  = 1 / (1 + np.exp(-raw))
        confidence = prob_fake * 100 if pred == 1 else (1 - prob_fake) * 100
        return {
            "prediction": "Fake" if pred == 1 else "Real",
            "confidence": round(confidence, 2),
            "model": FUSION_MODEL_NAME,
            
            "raw_score": round(
                prob_fake if pred == 1 else (1 - prob_fake),
                4
            ),
            
            "image_score": float(prob_fake),
            "image_confidence": float(confidence / 100)
        }

    def _extract_deep_features(self, path: str, extractor) -> np.ndarray:
        import torch
        from PIL import Image

        img = Image.open(path).convert("RGB").resize(FUSION_INPUT_SIZE)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - _MEAN) / _STD
        tensor = torch.tensor(arr).permute(2, 0, 1).unsqueeze(0)

        with torch.no_grad():
            features = extractor(tensor)
            if hasattr(features, "cpu"):
                features = features.cpu()
            deep_feats = features.numpy().reshape(-1)

        return deep_feats

    def _extract_landmark_features(self, path: str, predictor) -> np.ndarray:
        import dlib
        from PIL import Image

        img = Image.open(path).convert("RGB")
        gray = np.array(img.convert("L"), dtype=np.uint8)
        detector = dlib.get_frontal_face_detector()
        faces = detector(gray, 1)

        if len(faces) == 0:
            logger.warning("[IMAGE-FUSION] No faces detected for landmark extraction.")
            return None

        faces = detector(gray, 1)
        
        if len(faces) == 0:
            logger.warning("[IMAGE-FUSION] No face detected.")
            return np.zeros(136, dtype=np.float32)
        
        face = max(faces, key=lambda r: r.width() * r.height())
        
        if face.width() < 30 or face.height() < 30:
            return np.zeros(136, dtype=np.float32)
        h, w = gray.shape
        landmarks = predictor(gray, face)
        
        features = []
        for i in range(68):
            part = landmarks.part(i)
            x = part.x / w
            y = part.y / h
            features.extend([x, y])
        return np.array(features, dtype=np.float32)

    def _preprocess(self, path: str) -> np.ndarray:
        """
        Load image from disk → PIL → resize → normalize.
        Returns array of shape (1, 224, 224, 3).
        """
        from PIL import Image
        img = Image.open(path).convert("RGB").resize(INPUT_SIZE)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - _MEAN) / _STD
        return np.expand_dims(arr, 0)

    def _format(self, raw: float) -> dict:
        is_fake    = raw >= self.threshold
        confidence = raw * 100 if is_fake else (1 - raw) * 100
        return {
            "prediction": "Fake" if is_fake else "Real",
            "confidence": round(confidence, 2),
            "model": MODEL_NAME,
            "raw_score": round(raw, 4),
            "image_score": float(raw),
            "image_confidence": float(confidence / 100)
        }
