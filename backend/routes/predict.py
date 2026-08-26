"""
routes/predict.py — The 3 prediction endpoints consumed by the React frontend.

Frontend (api.js) calls:
    POST /predict/image   multipart/form-data  field: file
    POST /predict/video   multipart/form-data  field: file
    POST /predict/audio   multipart/form-data  field: file

Expected response shape (api.js reads these exact keys):
    {
        "prediction":      "Fake" | "Real",
        "confidence":      97.3,
        "processing_time": "1.2s",
        "model":           "EfficientNet-B4"
    }

Error shape:
    { "detail": "Human-readable error message" }
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app

from services.file_validator import FileValidator
from services.predict_service import PredictService
from utils.file_utils import save_temp_file, delete_file

from services.fusion_runner import FusionRunner
from services.model_registry import ModelRegistry

logger = logging.getLogger(__name__)
predict_bp = Blueprint("predict", __name__, url_prefix="/predict")


# ── Shared helper ─────────────────────────────────────────────────────────────

def _run_prediction(media_type: str):
    """
    Shared pipeline for image/video/audio endpoints:
    1. Validate incoming file
    2. Save to temp
    3. Run model inference
    4. Remove internal non-JSON objects
    5. Clean up temp file
    6. Return JSON matching frontend contract
    """

    logger.info(
        f"[{media_type.upper()}] Prediction request received"
    )

    # 1. File presence check
    if "file" not in request.files:
        logger.warning(
            f"[{media_type.upper()}] No 'file' field in request"
        )

        return jsonify({
            "detail": (
                "No file provided. Send a multipart/form-data "
                "request with a 'file' field."
            )
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "detail": "No file selected."
        }), 400

    # 2. Validate MIME type and size
    validator = FileValidator(
        current_app.config
    )

    validation_error = validator.validate(
        file,
        media_type
    )

    if validation_error:

        logger.warning(
            f"[{media_type.upper()}] "
            f"Validation failed: {validation_error}"
        )

        return jsonify({
            "detail": validation_error
        }), 422

    # 3. Save temporary file
    tmp_path = None

    try:

        tmp_path = save_temp_file(
            file_storage=file,
            upload_dir=current_app.config[
                "UPLOAD_FOLDER"
            ],
            original_filename=file.filename,
        )

        # 4. Run inference
        service = PredictService(
            current_app.config
        )

        result = service.predict(
            media_type,
            tmp_path,
            file.filename
        )

        logger.info(
            f"[{media_type.upper()}] Done | "
            f"file={file.filename} | "
            f"prediction={result['prediction']} | "
            f"confidence={result['confidence']}"
        )

        # IMPORTANT:
        # VideoRunner keeps PIL.Image frames internally for
        # multimodal/fusion processing. PIL.Image cannot be
        # serialized by Flask's jsonify().
        #
        # Remove them only from the HTTP response.
        result.pop("frames", None)

        # Also remove any accidental internal image objects
        # if a future runner adds them under these keys.
        result.pop("frame_images", None)
        result.pop("images", None)

        # 5. Return JSON
        return jsonify(result), 200

    except RuntimeError as exc:

        logger.error(
            f"[{media_type.upper()}] "
            f"Inference error: {exc}",
            exc_info=True
        )

        return jsonify({
            "detail": str(exc)
        }), 500

    except Exception as exc:

        logger.error(
            f"[{media_type.upper()}] "
            f"Unexpected error: {exc}",
            exc_info=True
        )

        return jsonify({
            "detail": (
                "An unexpected error occurred "
                "during analysis."
            )
        }), 500

    finally:

        if (
            tmp_path
            and os.path.exists(tmp_path)
        ):
            delete_file(tmp_path)


# ── Image endpoint ────────────────────────────────────────────────────────────

@predict_bp.post("/image")
def predict_image():

    """
    POST /predict/image

    Accepts:
        JPG, PNG, WEBP, GIF, BMP

    Model:
        EfficientNet-B4
    """

    return _run_prediction("image")


# ── Video endpoint ────────────────────────────────────────────────────────────

@predict_bp.post("/video")
def predict_video():

    """
    POST /predict/video

    Accepts:
        MP4, AVI, MOV, MKV, WEBM

    Model:
        Fine-tuned SigLIP V2 deepfake detector.
    """

    return _run_prediction("video")


# ── Audio endpoint ────────────────────────────────────────────────────────────

@predict_bp.post("/audio")
def predict_audio():

    """
    POST /predict/audio

    Accepts:
        MP3, WAV, FLAC, OGG, M4A

    Model:
        CNN on Log-Mel spectrograms.
    """

    return _run_prediction("audio")


# ── Multimodal endpoint ───────────────────────────────────────────────────────

@predict_bp.post("/multimodal")
def predict_multimodal():

    logger.info(
        "[MULTIMODAL] Prediction request received"
    )

    if "file" not in request.files:

        return jsonify({
            "detail": "No file provided."
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "detail": "No file selected."
        }), 400

    tmp_path = None

    try:

        tmp_path = save_temp_file(
            file_storage=file,
            upload_dir=current_app.config[
                "UPLOAD_FOLDER"
            ],
            original_filename=file.filename,
        )

        registry = ModelRegistry.get_instance()

        fusion_runner = FusionRunner(
            registry,
            current_app.config
        )

        result = fusion_runner.run(
            tmp_path,
            file.filename
        )

        # Remove PIL.Image objects or other internal data
        # before returning JSON.
        if isinstance(result, dict):
            result.pop("frames", None)
            result.pop("frame_images", None)
            result.pop("images", None)

        return jsonify(result), 200

    except Exception as exc:

        logger.error(
            f"[MULTIMODAL] Error: {exc}",
            exc_info=True
        )

        return jsonify({
            "detail": str(exc)
        }), 500

    finally:

        if (
            tmp_path
            and os.path.exists(tmp_path)
        ):
            delete_file(tmp_path)
