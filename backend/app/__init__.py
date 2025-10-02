from flask import Flask

from .routes import api_bp


def create_app() -> Flask:
    """Flask アプリケーションを生成して API Blueprint を登録する。"""
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
