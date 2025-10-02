from pathlib import Path

from app.schemas import Task


def test_sample_tasks_loadable():
    data_path = Path(__file__).parent / "data" / "sample_tasks.json"
    payloads = Task.load_many(data_path)
    assert isinstance(payloads, list)
    assert payloads, "サンプルタスクが空です"
    for task in payloads:
        assert "id" in task
        assert "title" in task
        assert "children" in task
