from __future__ import annotations

from pathlib import Path

from flask import Flask, Response, send_from_directory

from .routes import api_bp

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
INDEX_HTML = FRONTEND_DIST / "index.html"


def create_app() -> Flask:
    """Flask アプリケーションを生成して API Blueprint を登録する。"""
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIST / "assets"),
        static_url_path="/assets",
    )
    app.config["JSON_AS_ASCII"] = False
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def serve_root() -> Response:
        """ビルド済みのフロントエンドをルートで提供する。"""
        if INDEX_HTML.exists():
            return send_from_directory(FRONTEND_DIST, "index.html")
        return Response(
            """
            <h1>フロントエンドがまだビルドされていません。</h1>
            <p>フロントエンド資産を配信するには <code>npm run build</code> を実行してください。</p>
            """.strip(),
            mimetype="text/html; charset=utf-8",
            status=503,
        )

    return app
