from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template

from .db import init_db
from .routes import api_bp


SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent / "tests" / "data" / "sample_tasks.json"


def create_app() -> Flask:
    """Flask アプリケーションを生成し、API と UI を統合する。"""

    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates",
    )
    app.register_blueprint(api_bp, url_prefix="/api")
    init_db(sample_data_path=SAMPLE_DATA_PATH)

    @app.get("/")
    def index() -> str:
        """シングルサーバー構成の UI を返す。"""

        return render_template("index.html")

    return app
