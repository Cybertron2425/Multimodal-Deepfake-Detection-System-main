"""
utils/error_handlers.py

Global Flask error handlers.
The React api.js interceptor reads:  error.response.data.detail
Every handler here returns { "detail": "<message>" }.
"""

import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(exc):
        logger.warning(f"400 Bad Request: {exc}")
        return jsonify({"detail": "Bad request. Check your request format and try again."}), 400

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"detail": f"Endpoint not found. Check the API URL."}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"detail": "Method not allowed. Use POST for prediction endpoints."}), 405

    @app.errorhandler(413)
    def request_entity_too_large(exc):
        return jsonify({
            "detail": "File too large. Maximum upload size is 500 MB."
        }), 413

    @app.errorhandler(422)
    def unprocessable(exc):
        return jsonify({"detail": "Unprocessable request. Validate the file type and size."}), 422

    @app.errorhandler(500)
    def internal_error(exc):
        logger.error(f"500 Internal Server Error: {exc}", exc_info=True)
        return jsonify({"detail": "Internal server error. Please try again."}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return jsonify({"detail": "An unexpected error occurred."}), 500
