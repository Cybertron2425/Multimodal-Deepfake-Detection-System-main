"""
routes/health.py — Health & status endpoints.
GET /health  → liveness probe
GET /status  → model load status
"""

from flask import Blueprint, jsonify, current_app
from services.model_registry import ModelRegistry

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def liveness():
    """Simple liveness probe — returns 200 if Flask is running."""
    return jsonify({"status": "ok", "service": "DeepScan API"}), 200


@health_bp.get("/status")
def model_status():
    """
    Returns which AI models are loaded and ready.
    The frontend Navbar shows '3 Models Active' — this is the source of truth.
    """
    registry = ModelRegistry.get_instance()
    return jsonify({
        "status":  "ok",
        "models": {
            "image": {
                "loaded": registry.image_loaded,
                "name":   "EfficientNet-B4",
                "path":   current_app.config["IMAGE_MODEL_PATH"],
            },
            "image_fusion": {
                "loaded": registry.image_fusion_loaded,
                "name":   "EfficientNet-B4 + Dlib + SVM Fusion",
                "path":   current_app.config["IMAGE_FUSION_SVM_PATH"],
            },
            "video": {
                "loaded": registry.video_loaded,
                "name":   "ResNeXt101-32x8d",
                "path":   current_app.config["VIDEO_MODEL_PATH"],
            },
            "audio": {
                "loaded": registry.audio_loaded,
                "name":   "CNN-LogMel (ASVspoof)",
                "path":   current_app.config["AUDIO_MODEL_PATH"],
            },
        },
        "active_count": sum([
            registry.image_loaded,
            registry.image_fusion_loaded,
            registry.video_loaded,
            registry.audio_loaded,
        ]),
    }), 200
