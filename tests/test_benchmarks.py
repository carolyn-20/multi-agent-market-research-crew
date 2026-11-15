import json
import time

from crew.benchmarks import BenchmarkLogger


class FakeOutput:
    name = None
    description = "Research the tech sector"
    agent = "Researcher"


class FakeStep:
    tool = "Web Search and Scrape"
    thought = "need data"


def test_logs_tasks_routing_and_appends_runs(tmp_path):
    path = tmp_path / "benchmarks.json"
    for _ in range(2):
        b = BenchmarkLogger("q", path)
        b.start()
        b.on_step(FakeStep())
        with b.timed("analysis", "Analyst"):
            time.sleep(0.01)
        b.on_task(FakeOutput())
        b.finish()
    runs = json.loads(path.read_text())["runs"]
    assert len(runs) == 2
    run = runs[-1]
    assert [t["agent"] for t in run["tasks"]] == ["Analyst", "Researcher"]
    assert run["tasks"][0]["seconds"] >= 0.01 and run["total_seconds"] > 0
    events = [r["event"] for r in run["routing_history"]]
    assert events == ["tool_call", "task_started", "task_completed", "task_completed"]


def test_corrupt_file_is_replaced(tmp_path):
    path = tmp_path / "benchmarks.json"
    path.write_text("{not json")
    BenchmarkLogger("q", path).finish()
    assert len(json.loads(path.read_text())["runs"]) == 1
