from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class Task:
    id: str
    title: str
    detail: str
    assignee: str
    owner: str
    start_date: date
    due_date: date
    status: str
    priority: str
    effort: str
    children: List["Task"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "detail": self.detail,
            "assignee": self.assignee,
            "owner": self.owner,
            "start_date": self.start_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "status": self.status,
            "priority": self.priority,
            "effort": self.effort,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Task":
        children = [cls.from_dict(child) for child in payload.get("children", [])]
        return cls(
            id=str(payload["id"]),
            title=str(payload["title"]),
            detail=str(payload.get("detail", "")),
            assignee=str(payload.get("assignee", "")),
            owner=str(payload.get("owner", "")),
            start_date=_parse_date(payload.get("start_date")),
            due_date=_parse_date(payload.get("due_date")),
            status=str(payload.get("status", "未着手")),
            priority=str(payload.get("priority", "中")),
            effort=str(payload.get("effort", "中")),
            children=children,
        )

    @classmethod
    def load_many(cls, path: Path) -> List[Dict[str, Any]]:
        import json

        with path.open("r", encoding="utf-8") as fp:
            raw_tasks: Iterable[Dict[str, Any]] = json.load(fp)
        return [cls.from_dict(task).to_dict() for task in raw_tasks]


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value).date()
    raise ValueError("日付は ISO 8601 形式で指定してください。")
