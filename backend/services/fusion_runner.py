from services.fusion.suspicious_frame_selector import select_suspicious_frames
from services.runners.video_runner import VideoRunner
from services.runners.audio_runner import AudioRunner
from services.runners.image_runner import ImageRunner

import os
import tempfile

from utils.audio_extractor import extract_audio

class FusionRunner:

    def __init__(self, registry, config):
        self.registry = registry
        self.config = config

        self.video_runner = VideoRunner(
            registry,
            config
        )

        self.audio_runner = AudioRunner(
            registry,
            config
        )

        self.image_runner = ImageRunner(
            registry,
            config
        )

    def run(self, file_path: str, filename: str):
        # Video branch
        video_result = self.video_runner.run(
            file_path,
            filename
        )
        
        print(
            "VIDEO SCORE =",
            video_result["video_score"]
        )
        
        
        top_frames = select_suspicious_frames(
            video_result["frames"],
            video_result["frame_probs"],
            top_k=3
        )
        
        print(
            "TOP FRAMES =",
            len(top_frames)
        )
        # Audio extraction
        temp_audio = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        temp_audio.close()

        audio_path = extract_audio(
            file_path,
            temp_audio.name
        )

        audio_result = None
        
        if audio_path is not None:
            audio_result = self.audio_runner.run(
                audio_path,
                "audio.wav"
            )
            print(
                "AUDIO SCORE =",
                audio_result["raw_score"]
            )
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            
            
        image_scores = []
        
        
        
        for frame in top_frames:
            score = self.image_runner.predict_pil(frame)
            image_scores.append(score)
            
        image_score = (
            sum(image_scores) / len(image_scores)
            if image_scores else 0.5
        )
            
        print("IMAGE SCORE =", image_score)
    
        # ===== MULTIMODAL FUSION =====

        video_score = video_result["video_score"]

        audio_score = 0.5
        if audio_result is not None:
            audio_score = audio_result["audio_score"]

        final_score = (
            0.85 * video_score +
            0.0 * image_score +
            0.15 * audio_score
        )

        prediction = "Fake" if final_score >= 0.5 else "Real"

        confidence = (
            final_score * 100
            if prediction == "Fake"
            else (1 - final_score) * 100
        )
        
        clean_video_result = dict(video_result)
        if "frames" in clean_video_result:
            del clean_video_result["frames"]
            
        return {
            "prediction": prediction,
            "confidence": round(confidence, 2),
        
            "model": "Multimodal Fusion",
            "raw_score": round(final_score, 4),
            "video_score": round(video_score, 4),
            "audio_score": round(audio_score, 4),
            "image_score": round(image_score, 4),
            "video_result": clean_video_result,
            "audio_result": audio_result,
        }