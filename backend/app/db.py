from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .schemas import Task


def get_database_path() -> Path:
    """環境変数から SQLite のファイルパスを解決する。"""
    env_path = os.getenv("TODO_DB_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "todo.sqlite3"


def get_connection() -> sqlite3.Connection:
    """SQLite への接続を生成する。"""
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    detail TEXT NOT NULL,
    assignee TEXT NOT NULL,
    owner TEXT NOT NULL,
    start_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    effort TEXT NOT NULL,
    parent_id TEXT REFERENCES tasks(id)
);
"""


def init_db(sample_data_path: Optional[Path] = None) -> None:
    """テーブルを作成し、必要に応じてサンプルデータを投入する。"""
    with closing(get_connection()) as conn:
        conn.execute(SCHEMA)
        conn.commit()

    with closing(get_connection()) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM tasks")
        (count,) = cur.fetchone()
        if count:
            return

        for task in _load_seed_tasks(sample_data_path):
            _insert_task(conn, task, parent_id=None)
        conn.commit()


def fetch_tasks() -> List[Dict[str, Any]]:
    """タスクを親子関係に展開したリストとして取得する。"""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, title, detail, assignee, owner, start_date, due_date, status, priority, effort, parent_id "
            "FROM tasks"
        ).fetchall()

    tasks = {row["id"]: _row_to_task(row) for row in rows}
    roots: List[Dict[str, Any]] = []

    for row in rows:
        task = tasks[row["id"]]
        parent_id = row["parent_id"]
        if parent_id and parent_id in tasks:
            tasks[parent_id]["children"].append(task)
        else:
            roots.append(task)

    for task in tasks.values():
        task["children"].sort(key=lambda t: (t["start_date"], t["id"]))
    roots.sort(key=lambda t: (t["start_date"], t["id"]))
    return roots


def insert_task(task: Task, parent_id: Optional[str] = None) -> None:
    """タスクを永続化する。子タスクも再帰的に登録する。"""
    with closing(get_connection()) as conn:
        _insert_task(conn, task.to_dict(), parent_id=parent_id)
        conn.commit()


def _insert_task(conn: sqlite3.Connection, task_payload: Dict[str, Any], parent_id: Optional[str]) -> None:
    conn.execute(
        """
        INSERT INTO tasks (
            id, title, detail, assignee, owner, start_date, due_date, status, priority, effort, parent_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_payload["id"],
            task_payload["title"],
            task_payload.get("detail", ""),
            task_payload.get("assignee", ""),
            task_payload.get("owner", ""),
            task_payload.get("start_date"),
            task_payload.get("due_date"),
            task_payload.get("status", "未着手"),
            task_payload.get("priority", "中"),
            task_payload.get("effort", "中"),
            parent_id,
        ),
    )

    for child in task_payload.get("children", []):
        _insert_task(conn, child, parent_id=task_payload["id"])


def _row_to_task(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "detail": row["detail"],
        "assignee": row["assignee"],
        "owner": row["owner"],
        "start_date": row["start_date"],
        "due_date": row["due_date"],
        "status": row["status"],
        "priority": row["priority"],
        "effort": row["effort"],
        "children": [],
    }


def _load_seed_tasks(sample_data_path: Optional[Path]) -> Iterable[Dict[str, Any]]:
    if sample_data_path and sample_data_path.exists():
        return Task.load_many(sample_data_path)
    return [_fallback_task()]


def _fallback_task() -> Dict[str, Any]:
    today = date.today()
    fallback = Task(
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
    return fallback.to_dict()
