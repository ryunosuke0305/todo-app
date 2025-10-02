from __future__ import annotations

from uuid import uuid4

from flask import Blueprint, abort, jsonify, request
from werkzeug.exceptions import HTTPException

from .db import delete_task, fetch_task, fetch_tasks, insert_task, update_task
from .schemas import Task


api_bp = Blueprint("api", __name__)


@api_bp.get("/tasks")
def list_tasks():
    """永続化されたタスク一覧を返却する。"""
    return jsonify({"tasks": fetch_tasks()})


@api_bp.get("/tasks/<task_id>")
def get_task(task_id: str):
    """指定したタスクを返却する。"""

    task = fetch_task(task_id)
    if task is None:
        abort(404, description="指定されたタスクが見つかりません。")
    return jsonify({"task": task})


@api_bp.post("/tasks")
def create_task():
    """タスクを新規作成する。"""

    payload = _get_json_payload()
    parent_id = _normalize_parent_id(payload.pop("parent_id", None))
    payload.setdefault("id", str(uuid4()))

    if parent_id:
        _ensure_parent_exists(parent_id)

    task = _load_task_from_payload(payload)
    insert_task(task, parent_id=parent_id)

    created = fetch_task(task.id)
    return jsonify({"task": created}), 201


@api_bp.put("/tasks/<task_id>")
def edit_task(task_id: str):
    """タスク情報を更新する。"""

    payload = _get_json_payload()
    parent_id = _normalize_parent_id(payload.pop("parent_id", None))

    if parent_id == task_id:
        abort(400, description="親タスクに自身を指定することはできません。")
    if parent_id:
        _ensure_parent_exists(parent_id)

    payload["id"] = task_id
    task = _load_task_from_payload(payload)

    if not update_task(task, parent_id=parent_id):
        abort(404, description="指定されたタスクが見つかりません。")

    updated = fetch_task(task_id)
    return jsonify({"task": updated})


@api_bp.delete("/tasks/<task_id>")
def remove_task(task_id: str):
    """タスクを削除する。"""

    if not delete_task(task_id):
        abort(404, description="指定されたタスクが見つかりません。")
    return jsonify({"deleted": True})


def _get_json_payload() -> dict:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400, description="有効な JSON ボディを指定してください。")
    return payload


def _load_task_from_payload(payload: dict) -> Task:
    try:
        return Task.from_dict(payload)
    except (KeyError, ValueError) as exc:
        abort(400, description=str(exc))


def _ensure_parent_exists(parent_id: str) -> None:
    if fetch_task(parent_id) is None:
        abort(400, description="指定された親タスクが存在しません。")


def _normalize_parent_id(parent_id: object) -> str | None:
    if parent_id in (None, ""):
        return None
    return str(parent_id)


@api_bp.errorhandler(HTTPException)
def _handle_http_exception(exc: HTTPException):
    response = jsonify({"message": exc.description})
    response.status_code = exc.code or 500
    return response
