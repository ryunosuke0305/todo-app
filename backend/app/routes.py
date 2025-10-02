from __future__ import annotations

from flask import Blueprint, jsonify

from .db import fetch_tasks


api_bp = Blueprint("api", __name__)


@api_bp.get("/tasks")
def list_tasks():
    """永続化されたタスク一覧を返却する。"""
    return jsonify({"tasks": fetch_tasks()})
