import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_DIR = Path(__file__).parent


class BaseConfig:
    SECRET_KEY          = os.getenv("SECRET_KEY", "change-me-in-production")
    JSON_SORT_KEYS      = False
    MAX_CONTENT_LENGTH  = 500 * 1024 * 1024   # 500 MB — matches frontend MAX_FILE_SIZE

    _cors_raw   = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

    UPLOAD_FOLDER   = os.getenv("UPLOAD_FOLDER",  str(BASE_DIR / "uploads"))
    MAX_FILE_MB     = 500

    ALLOWED_IMAGE_TYPES = {
        "image/jpeg", "image/png", "image/webp",
        "image/gif", "image/bmp",
    }
    ALLOWED_VIDEO_TYPES = {
        "video/mp4", "video/x-msvideo", "video/quicktime",
        "video/x-matroska", "video/webm",
    }
    ALLOWED_AUDIO_TYPES = {
        "audio/mpeg", "audio/wav", "audio/x-wav",
        "audio/flac", "audio/ogg", "audio/mp4",
        "audio/x-m4a", "audio/aac",
    }

    MODELS_DIR          = os.getenv("MODELS_DIR",  str(BASE_DIR / "models" / "weights"))
    IMAGE_MODEL_PATH    = os.getenv("IMAGE_MODEL_PATH",
                                    str(BASE_DIR / "models" / "weights" / "best_image_model.keras"))
    VIDEO_MODEL_PATH    = os.getenv("VIDEO_MODEL_PATH",
                                    str(BASE_DIR / "models" / "weights" / "improved_video_model.pth"))
    AUDIO_MODEL_PATH    = os.getenv("AUDIO_MODEL_PATH",
                                    str(BASE_DIR / "models" / "weights" / "best_audio_model.keras"))

    IMAGE_FUSION_SVM_PATH         = os.getenv("IMAGE_FUSION_SVM_PATH",
                                    str(BASE_DIR / "models" / "weights" / "svm_efficientnet_b4.pkl"))
    IMAGE_FUSION_PCA_PATH         = os.getenv("IMAGE_FUSION_PCA_PATH",
                                    str(BASE_DIR / "models" / "weights" / "pca_efficientnet_b4.pkl"))
    IMAGE_FUSION_DEEP_SCALER_PATH = os.getenv("IMAGE_FUSION_DEEP_SCALER_PATH",
                                    str(BASE_DIR / "models" / "weights" / "deep_scaler.pkl"))
    IMAGE_FUSION_LAND_SCALER_PATH = os.getenv("IMAGE_FUSION_LAND_SCALER_PATH",
                                    str(BASE_DIR / "models" / "weights" / "land_scaler.pkl"))
    IMAGE_FUSION_LANDMARK_PATH    = os.getenv("IMAGE_FUSION_LANDMARK_PATH",
                                    str(BASE_DIR / "models" / "weights" / "shape_predictor_68_face_landmarks.dat"))

    IMAGE_FAKE_THRESHOLD = float(os.getenv("IMAGE_FAKE_THRESHOLD", "0.5"))
    VIDEO_FAKE_THRESHOLD = float(os.getenv("VIDEO_FAKE_THRESHOLD", "0.30"))
    AUDIO_FAKE_THRESHOLD = float(os.getenv("AUDIO_FAKE_THRESHOLD", "0.5"))
    VIDEO_FRAME_COUNT    = int(os.getenv("VIDEO_FRAME_COUNT", "16"))

    LOG_LEVEL   = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR     = os.getenv("LOG_DIR",   str(BASE_DIR / "logs"))


class DevelopmentConfig(BaseConfig):
    ENV   = "development"
    DEBUG = True


class ProductionConfig(BaseConfig):
    ENV   = "production"
    DEBUG = False


class TestingConfig(BaseConfig):
    ENV     = "testing"
    TESTING = True
    DEBUG   = True
    # Use an in-memory temp dir in tests
    UPLOAD_FOLDER = "/tmp/deepscan_test_uploads"


_configs = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}


def get_config(name: str = "development"):
    return _configs.get(name, DevelopmentConfig)
