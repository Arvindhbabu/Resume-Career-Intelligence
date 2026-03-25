"""
ResumeIQ - AI-Powered Resume Analyzer & Job Recommendation System
Main Flask Application Entry Point
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__, template_folder="../frontend/templates",
                static_folder="../frontend/static")

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///resumeiq.db"
    ).replace("postgres://", "postgresql://")   # Render fix
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload cap
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "../data/uploads")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Extensions ─────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # ── Register Blueprints ────────────────────────────────────────────────────
    from backend.api.routes import api_bp
    from backend.api.views import views_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(views_bp)

    # ── DB Init ────────────────────────────────────────────────────────────────
    with app.app_context():
        from backend.database import models  # noqa: F401 – registers models
        db.create_all()

    # ── Global error handlers ──────────────────────────────────────────────────
    @app.errorhandler(413)
    def too_large(e):
        return jsonify(error="File too large. Max 5 MB."), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Resource not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal server error."), 500

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false") == "true")
