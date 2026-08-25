"""
DeepScan — Flask Backend
Entry point. Run with: python app.py
"""


import tensorflow as tf
print("TF LOADED AT STARTUP", tf.__version__)

import os
import logging
from flask import Flask
from flask_cors import CORS

from config import get_config
from routes.predict import predict_bp
from routes.health import health_bp
from utils.error_handlers import register_error_handlers
from utils.logger import setup_logger


def create_app(config_name: str = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)

    # ── Load config ──────────────────────────────────────────────────────────
    cfg = get_config(config_name or os.getenv("FLASK_ENV", "development"))
    app.config.from_object(cfg)

    # ── Logging ──────────────────────────────────────────────────────────────
    setup_logger(app)

    # ── CORS — allow React dev server and production origin ──────────────────
    CORS(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    # ── Ensure upload directory exists ───────────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Register blueprints ──────────────────────────────────────────────────
    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)

    # ── Register error handlers ──────────────────────────────────────────────
    register_error_handlers(app)

    app.logger.info(
        f"DeepScan backend started | env={app.config['ENV']} | "
        f"models_dir={app.config['MODELS_DIR']}"
    )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=app.config.get("DEBUG", False),
        use_reloader=False,   # reloader causes models to load twice
    )
