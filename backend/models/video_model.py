"""
Video Deepfake Detector
Model: ResNeXt101 fine-tuned on FaceForensics++ C23
Pipeline: MTCNN face extraction → ResNeXt101 per-frame → voting
Input: any video file
Output: prediction, confidence (fake frame ratio), processing_time
"""

import os
import io
import time
import logging
import tempfile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_PATH   = Path(os.getenv("VIDEO_MODEL_PATH", "models/best_resnext101_deepfake.pth"))
FRAME_COUNT  = int(os.getenv("VIDEO_FRAME_COUNT", "16"))
FAKE_THRESH  = float(os.getenv("VIDEO_FAKE_THRESHOLD", "0.30"))

_model  = None
_device = None
_mtcnn  = None
_transform = None
_MODEL_LOADED = False


# ── Lazy imports ──────────────────────────────────────────────────────────────
def _get_device():
    global _device
    if _device is None:
        import torch
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"[VIDEO] Using device: {_device}")
    return _device


def _get_transform():
    global _transform
    if _transform is None:
        from torchvision import transforms
        _transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                  [0.229, 0.224, 0.225]),
        ])
    return _transform


def _build_resnext(torch, models):
    """Build ResNeXt-101 with 2-class head (same arch as training notebook)."""
    import torch.nn as nn
    model = models.resnext101_32x8d(weights=None)
    # Unfreeze last two layer groups as in training
    for name, param in model.named_parameters():
        param.requires_grad = any(k in name for k in ("layer3", "layer4", "fc"))
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.fc.in_features, 2),
    )
    return model


def load_model():
    global _model, _MODEL_LOADED
    if _MODEL_LOADED:
        return _model

    import torch
    from torchvision import models

    device = _get_device()
    net = _build_resnext(torch, models)

    if MODEL_PATH.exists():
        logger.info(f"[VIDEO] Loading weights from {MODEL_PATH}")
        try:
            state = torch.load(str(MODEL_PATH), map_location=device)
            net.load_state_dict(state)
            logger.info("[VIDEO] Weights loaded.")
        except Exception as e:
            logger.warning(f"[VIDEO] Could not load weights: {e}. Demo mode.")
    else:
        logger.warning(f"[VIDEO] No model file at {MODEL_PATH}. Running DEMO mode.")

    net.to(device).eval()
    _model = net
    _MODEL_LOADED = True
    return _model


def _get_mtcnn():
    global _mtcnn
    if _mtcnn is None:
        from facenet_pytorch import MTCNN
        device = _get_device()
        _mtcnn = MTCNN(
            image_size=224, margin=20, min_face_size=40,
            keep_all=False, device=device, post_process=False,
        )
    return _mtcnn


def _extract_faces(video_path: str, frame_count: int = FRAME_COUNT):
    """Sample frames uniformly → MTCNN face detection → list of PIL Images."""
    import cv2
    from PIL import Image

    cap   = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap.release()
        return []

    indices = np.linspace(0, total - 1, frame_count, dtype=int)
    frames  = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            continue
        frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    cap.release()

    if not frames:
        return []

    mtcnn = _get_mtcnn()
    faces = []
    batch_size = 16
    for i in range(0, len(frames), batch_size):
        batch = frames[i: i + batch_size]
        try:
            ft = mtcnn(batch)
            if ft is None:
                continue
            if not isinstance(ft, list):
                ft = [ft]
            for f in ft:
                if f is None:
                    continue
                face_np = f.permute(1, 2, 0).byte().cpu().numpy()
                faces.append(Image.fromarray(face_np))
        except Exception:
            continue
    return faces


def predict(file_bytes: bytes) -> dict:
    """Run deepfake detection on a video file."""
    t0 = time.perf_counter()

    # Write to temp file so cv2 can open it
    suffix = ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        import torch
        import torch.nn.functional as F

        model    = load_model()
        device   = _get_device()
        transform = _get_transform()

        faces = _extract_faces(tmp_path, FRAME_COUNT)

        if not faces:
            logger.warning("[VIDEO] No faces detected; defaulting to REAL.")
            elapsed = time.perf_counter() - t0
            return {
                "prediction":      "Real",
                "confidence":      50.0,
                "processing_time": f"{elapsed:.2f}s",
                "model":           "ResNeXt101 (no face)",
                "raw_score":       0.0,
                "frames_analyzed": 0,
            }

        fake_probs = []
        with torch.no_grad():
            for face in faces:
                tensor = transform(face).unsqueeze(0).to(device)
                logits = model(tensor)
                probs  = F.softmax(logits, dim=1).cpu().numpy()[0]
                fake_probs.append(float(probs[1]))

        fake_ratio = sum(1 for p in fake_probs if p > 0.5) / len(fake_probs)
        logger.info(f"FAKE FRAME RATIO = {fake_ratio}")
        logger.info(f"FRAME PROBS = {fake_probs}")
        is_fake    = fake_ratio >= FAKE_THRESH
        confidence = fake_ratio * 100 if is_fake else (1 - fake_ratio) * 100

        elapsed = time.perf_counter() - t0
        return {
            "prediction":      "Fake" if is_fake else "Real",
            "confidence":      round(confidence, 2),
            "processing_time": f"{elapsed:.2f}s",
            "model":           "ResNeXt101-32x8d",
            "raw_score":       round(fake_ratio, 4),
            "frames_analyzed": len(fake_probs),
            "per_frame_probs": [round(p, 3) for p in fake_probs],
        }
    finally:
        os.unlink(tmp_path)
