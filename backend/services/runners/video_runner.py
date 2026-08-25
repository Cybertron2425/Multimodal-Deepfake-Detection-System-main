"""
services/runners/video_runner.py

ResNeXt101-32x8d video deepfake detection.
Pipeline mirrors video_model_.py (notebook) exactly:
  1. Sample FRAME_COUNT frames uniformly across the video
  2. MTCNN face detection + alignment (224×224, margin=20)
  3. Per-frame softmax → fake probability
  4. Vote: if fake_frame_ratio >= FAKE_THRESHOLD → FAKE
"""

import logging
from tkinter import Image
import cv2
import cv2
import numpy as np
import cv2
from PIL import Image

from services.fusion.suspicious_frame_selector import (
    select_suspicious_frames
)



logger = logging.getLogger(__name__)

MODEL_NAME  = "ResNeXt101-32x8d"
INPUT_SIZE  = (224, 224)

# ImageNet normalization
_MEAN = [0.485, 0.456, 0.406]
_STD  = [0.229, 0.224, 0.225]


class VideoRunner:
    def __init__(self, registry, config: dict):
        self.registry     = registry
        self.config       = config
        self.frame_count  = int(config.get("VIDEO_FRAME_COUNT", 16))
        self.fake_thresh  = float(config.get("VIDEO_FAKE_THRESHOLD", 0.60))

    def run(self, file_path: str, filename: str) -> dict:
        import torch
        import torch.nn.functional as F
        from torchvision import transforms

        model  = self.registry.get_video_model(self.config)
        device = next(model.parameters()).device

        transform = transforms.Compose([
            transforms.Resize(INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(_MEAN, _STD),
        ])
        
        frames = self._extract_frames(file_path)

        faces = self._extract_faces(file_path)

        if not faces:
            logger.warning(f"[VIDEO] No faces detected in {filename}. Returning Real/50%.")
            return {
                "prediction": "Real",
                "confidence": 50.0,
                "model": MODEL_NAME,
                "raw_score": 0.0,
                "video_score": 0.0,
                "video_confidence": 0.0,
                "fake_ratio": 0.0,
                "frame_probs": [],
                "frames_analyzed": 0,
                "note": "No faces detected in video",
            }

        fake_probs = []
        model.eval()
        with torch.no_grad():
            for face_pil in faces:
                tensor = transform(face_pil).unsqueeze(0).to(device)
                logits = model(tensor)
                probs  = F.softmax(logits, dim=1).cpu().numpy()[0]
                fake_probs.append(float(probs[1]))
                logger.info(f"REAL={probs[0]:.4f} FAKE={probs[1]:.4f}")

        fake_ratio = sum(1 for p in fake_probs if p > 0.5) / len(fake_probs)
        logger.info(f"FAKE FRAME RATIO = {fake_ratio}")
        logger.info(f"FRAME PROBS = {fake_probs}")
        is_fake    = fake_ratio >= self.fake_thresh
        confidence = fake_ratio * 100 if is_fake else (1 - fake_ratio) * 100
        
        logger.info(f"TOTAL FRAMES = {len(frames)}")
        logger.info(f"TOTAL PROBS = {len(fake_probs)}")

        return {
            "prediction": "Fake" if is_fake else "Real",
            "confidence": round(confidence, 2),
            "model": MODEL_NAME,
            "raw_score": round(fake_ratio, 4),
            
            "video_score": float(np.mean(fake_probs)),
            "video_confidence": float(confidence / 100),
            
            "fake_ratio": float(fake_ratio),
            
            "frame_probs": fake_probs,
            "frames": frames,
            
            "frames_analyzed": len(fake_probs),
        }

    def _extract_faces(self, video_path: str):
        """
        Sample frames uniformly → MTCNN face extraction.
        Matches the extract_faces_from_video() function in the notebook.
        Returns list of PIL Images (face crops at 224×224).
        """
        import cv2
        from PIL import Image
        try:
            from facenet_pytorch import MTCNN
            import torch
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            mtcnn  = MTCNN(
                image_size=224, margin=20, min_face_size=40,
                keep_all=False, device=device, post_process=False,
            )
            has_mtcnn = True
        except ImportError:
            logger.warning("[VIDEO] facenet-pytorch not installed. Using centre-crop fallback.")
            has_mtcnn = False

        cap   = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total == 0:
            cap.release()
            return []

        indices = np.linspace(0, total - 1, self.frame_count, dtype=int)
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

        if not has_mtcnn:
            # Fallback: just centre-crop each frame
            return [f.resize(INPUT_SIZE) for f in frames]

        # Batch MTCNN — matches notebook batch_size=16 on CPU
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
            except Exception as exc:
                logger.debug(f"[VIDEO] MTCNN batch error: {exc}")
                continue

        return faces if faces else [f.resize(INPUT_SIZE) for f in frames]
    
    
    
    def _extract_frames(self, video_path: str):
        import cv2
        from PIL import Image
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total == 0:
            cap.release()
            return []
        
        indices = np.linspace(
            0,
            total - 1,
            self.frame_count,
            dtype=int
        )
        
        frames = []
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            frames.append(
                Image.fromarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                )
           )
        cap.release()
        return frames
    
    
    


