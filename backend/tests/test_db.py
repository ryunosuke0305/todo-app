from __future__ import annotations

import importlib
from pathlib import Path

from app import db


def test_init_db_loads_sample_data(tmp_path, monkeypatch):
    db_path = tmp_path / "tasks.sqlite3"
    monkeypatch.setenv("TODO_DB_PATH", str(db_path))
    importlib.reload(db)

    sample_path = Path(__file__).parent / "data" / "sample_tasks.json"
    db.init_db(sample_data_path=sample_path)

    tasks = db.fetch_tasks()
    assert tasks, "初期データのロードに失敗しました"
    root_ids = {task["id"] for task in tasks}
    assert "task-001" in root_ids
    assert "task-002" in root_ids

    parent = next(task for task in tasks if task["id"] == "task-001")
    child_ids = {child["id"] for child in parent["children"]}
    assert child_ids == {"task-001-1", "task-001-2"}


def test_init_db_uses_fallback_when_sample_missing(tmp_path, monkeypatch):
    db_path = tmp_path / "fallback.sqlite3"
    monkeypatch.setenv("TODO_DB_PATH", str(db_path))
    importlib.reload(db)

    missing_sample = tmp_path / "missing.json"
    db.init_db(sample_data_path=missing_sample)

    tasks = db.fetch_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] == "fallback"
    assert tasks[0]["children"] == []
