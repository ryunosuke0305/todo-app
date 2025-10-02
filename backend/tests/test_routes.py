from __future__ import annotations

import importlib
from datetime import date, timedelta
from pathlib import Path

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "api.sqlite3"
    monkeypatch.setenv("TODO_DB_PATH", str(db_path))

    from app import db as db_module
    import app as app_package

    importlib.reload(db_module)
    importlib.reload(app_package)

    sample_path = Path(__file__).parent / "data" / "sample_tasks.json"
    db_module.init_db(sample_data_path=sample_path)

    app = app_package.create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_task_crud_api(client):
    today = date.today()
    payload = {
        "title": "API登録タスク",
        "detail": "API経由で登録します",
        "assignee": "山田",
        "owner": "佐藤",
        "start_date": today.isoformat(),
        "due_date": (today + timedelta(days=5)).isoformat(),
        "status": "未着手",
        "priority": "中",
        "effort": "中",
    }

    create_resp = client.post("/api/tasks", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.get_json()["task"]
    task_id = created["id"]
    assert created["title"] == payload["title"]
    assert created["parent_id"] is None

    list_resp = client.get("/api/tasks")
    assert list_resp.status_code == 200
    tasks = list_resp.get_json()["tasks"]
    assert any(task["id"] == task_id for task in tasks)

    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["task"]["id"] == task_id

    update_payload = {
        **payload,
        "status": "作業中",
        "priority": "高",
        "effort": "大",
    }
    update_resp = client.put(f"/api/tasks/{task_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.get_json()["task"]
    assert updated["status"] == "作業中"
    assert updated["priority"] == "高"
    assert updated["effort"] == "大"

    delete_resp = client.delete(f"/api/tasks/{task_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()["deleted"] is True

    missing_resp = client.get(f"/api/tasks/{task_id}")
    assert missing_resp.status_code == 404
