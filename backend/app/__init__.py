from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from flask import Flask, send_from_directory

from .routes import api_bp


def create_app() -> Flask:
    """Flask アプリケーションを生成して API Blueprint を登録する。"""
    frontend_dist = _resolve_frontend_dist()
    static_folder = str(frontend_dist) if frontend_dist else None
    app = Flask(__name__, static_folder=static_folder, static_url_path="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    if frontend_dist:
        _register_frontend_routes(app, frontend_dist)
    else:
        _register_frontend_placeholder(app)
    return app


def _resolve_frontend_dist() -> Optional[Path]:
    """フロントエンドのビルド成果物を格納したディレクトリを推測する。"""

    candidates = []
    env_path = os.getenv("FRONTEND_DIST_DIR")
    if env_path:
        candidates.append(Path(env_path))

    base_backend_dir = Path(__file__).resolve().parents[1]
    repo_root = base_backend_dir.parent
    candidates.extend(
        [
            repo_root / "frontend" / "dist",
            repo_root / "frontend_dist",
            base_backend_dir / "frontend_dist",
        ]
    )

    for candidate in candidates:
        index_file = candidate / "index.html"
        if index_file.is_file():
            return candidate
    return None


def _register_frontend_routes(app: Flask, dist_dir: Path) -> None:
    """Vue.js のビルド成果物を返却するルートを登録する。"""

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path: str) -> object:  # pragma: no cover - flask response types vary
        target = dist_dir / path
        if target.exists() and target.is_file():
            return send_from_directory(dist_dir, path)
        return send_from_directory(dist_dir, "index.html")


def _register_frontend_placeholder(app: Flask) -> None:
    """フロントエンドのビルド成果物が存在しない場合のプレースホルダーを登録する。"""

    @app.get("/")
    def frontend_not_ready() -> tuple[dict[str, str], int]:
        return (
            {
                "message": "Frontend build artifacts not found. Please run 'npm run build'.",
            },
            503,
        )
