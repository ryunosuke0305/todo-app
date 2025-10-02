from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from flask import Blueprint, jsonify

from .schemas import Task

DATA_PATH = Path(__file__).resolve().parent.parent / "tests" / "data" / "sample_tasks.json"

api_bp = Blueprint("api", __name__)


def _load_sample_tasks() -> List[Dict[str, Any]]:
    if DATA_PATH.exists():
        return Task.load_many(DATA_PATH)
    today = date.today()
    fallback_task = Task(
        id="fallback",
        title="サンプルタスク",
        detail="サンプルデータファイルが存在しません。",
        assignee="未設定",
        owner="未設定",
        start_date=today,
        due_date=today,
        status="未着手",
        priority="中",
        effort="中",
        children=[],
    )
    return [fallback_task.to_dict()]


@api_bp.get("/tasks")
def list_tasks():
    """タスクのサンプルデータを返却する。"""
    return jsonify({"tasks": _load_sample_tasks()})
