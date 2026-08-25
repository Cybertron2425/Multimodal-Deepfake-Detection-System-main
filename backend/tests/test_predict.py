"""
tests/test_predict.py

Run with: python -m pytest tests/ -v
Covers:
  - All 3 predict endpoints (happy path + error cases)
  - File validator
  - Error response shape matches frontend expectation (detail key)
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


FAKE_RESULT = {
    "prediction":      "Fake",
    "confidence":      97.3,
    "processing_time": "1.20s",
    "model":           "EfficientNet-B4",
}

REAL_RESULT = {
    "prediction":      "Real",
    "confidence":      88.5,
    "processing_time": "0.90s",
    "model":           "EfficientNet-B4",
}


def _make_file(content=b"data", filename="test.jpg", content_type="image/jpeg"):
    return (io.BytesIO(content), filename), content_type


# ── Health endpoints ──────────────────────────────────────────────────────────

def test_health_liveness(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"


def test_health_status(client):
    res = client.get("/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "models" in body
    assert set(body["models"].keys()) == {"image", "image_fusion", "video", "audio"}


# ── /predict/image ────────────────────────────────────────────────────────────

class TestPredictImage:

    def test_no_file_returns_400(self, client):
        res = client.post("/predict/image")
        assert res.status_code == 400
        assert "detail" in res.get_json()

    def test_wrong_mime_returns_422(self, client):
        data = {"file": (io.BytesIO(b"audio"), "test.mp3", "audio/mpeg")}
        res  = client.post(
            "/predict/image",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 422
        assert "detail" in res.get_json()

    @patch("services.predict_service.PredictService.predict", return_value=FAKE_RESULT)
    def test_valid_image_returns_result(self, mock_predict, client):
        data = {"file": (io.BytesIO(b"\xff\xd8\xff" * 100), "photo.jpg", "image/jpeg")}
        res  = client.post(
            "/predict/image",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 200
        body = res.get_json()
        # Frontend reads exactly these 4 keys
        assert body["prediction"] in ("Fake", "Real")
        assert isinstance(body["confidence"], float)
        assert "processing_time" in body
        assert "model" in body

    @patch("services.predict_service.PredictService.predict", return_value=REAL_RESULT)
    def test_real_image_response_shape(self, mock_predict, client):
        data = {"file": (io.BytesIO(b"\x89PNG" * 50), "img.png", "image/png")}
        res  = client.post(
            "/predict/image",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 200
        body = res.get_json()
        assert body["prediction"] == "Real"
        assert body["confidence"] == 88.5


# ── /predict/video ────────────────────────────────────────────────────────────

class TestPredictVideo:

    def test_no_file_returns_400(self, client):
        res = client.post("/predict/video")
        assert res.status_code == 400
        assert "detail" in res.get_json()

    def test_image_file_on_video_endpoint_returns_422(self, client):
        data = {"file": (io.BytesIO(b"img"), "photo.jpg", "image/jpeg")}
        res  = client.post(
            "/predict/video",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 422

    @patch("services.predict_service.PredictService.predict", return_value={
        **FAKE_RESULT, "model": "ResNeXt101-32x8d", "frames_analyzed": 12,
    })
    def test_valid_video_returns_result(self, mock_predict, client):
        data = {"file": (io.BytesIO(b"\x00" * 1024), "clip.mp4", "video/mp4")}
        res  = client.post(
            "/predict/video",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 200
        body = res.get_json()
        assert body["prediction"] in ("Fake", "Real")
        assert "confidence" in body


# ── /predict/audio ────────────────────────────────────────────────────────────

class TestPredictAudio:

    def test_no_file_returns_400(self, client):
        res = client.post("/predict/audio")
        assert res.status_code == 400
        assert "detail" in res.get_json()

    @patch("services.predict_service.PredictService.predict", return_value={
        **FAKE_RESULT, "model": "CNN-LogMel (ASVspoof)",
    })
    def test_valid_audio_returns_result(self, mock_predict, client):
        data = {"file": (io.BytesIO(b"\x00" * 512), "voice.wav", "audio/wav")}
        res  = client.post(
            "/predict/audio",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 200
        body = res.get_json()
        assert body["prediction"] in ("Fake", "Real")
        assert isinstance(body["confidence"], float)


# ── Error shape ───────────────────────────────────────────────────────────────

class TestErrorShape:
    """All errors must contain 'detail' key — consumed by api.js interceptor."""

    def test_404_has_detail(self, client):
        res = client.get("/nonexistent")
        assert "detail" in res.get_json()

    def test_405_has_detail(self, client):
        res = client.get("/predict/image")   # GET not allowed
        assert "detail" in res.get_json()

    def test_400_image_no_file_has_detail(self, client):
        res = client.post("/predict/image")
        assert "detail" in res.get_json()


# ── File validator unit tests ─────────────────────────────────────────────────

class TestFileValidator:

    def _make_storage(self, content_type, size_bytes=1024):
        from werkzeug.datastructures import FileStorage
        from unittest.mock import MagicMock
        mock = MagicMock(spec=FileStorage)
        mock.content_type = content_type
        mock.stream = io.BytesIO(b"x" * size_bytes)
        return mock

    def test_valid_image_mime(self):
        from services.file_validator import FileValidator
        config = {
            "ALLOWED_IMAGE_TYPES": {"image/jpeg", "image/png"},
            "MAX_CONTENT_LENGTH": 500 * 1024 * 1024,
        }
        v   = FileValidator(config)
        err = v.validate(self._make_storage("image/jpeg"), "image")
        assert err is None

    def test_invalid_mime_returns_error(self):
        from services.file_validator import FileValidator
        config = {
            "ALLOWED_IMAGE_TYPES": {"image/jpeg"},
            "MAX_CONTENT_LENGTH": 500 * 1024 * 1024,
        }
        v   = FileValidator(config)
        err = v.validate(self._make_storage("application/pdf"), "image")
        assert err is not None
        assert "Invalid file type" in err

    def test_oversized_file_returns_error(self):
        from services.file_validator import FileValidator
        config = {
            "ALLOWED_IMAGE_TYPES": {"image/jpeg"},
            "MAX_CONTENT_LENGTH": 10,   # 10 bytes max
        }
        v   = FileValidator(config)
        err = v.validate(self._make_storage("image/jpeg", size_bytes=100), "image")
        assert err is not None
        assert "too large" in err.lower()
