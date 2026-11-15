"""Execution benchmarking: per-task timings + routing trace, persisted to benchmarks.json."""
from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class BenchmarkLogger:
    def __init__(self, query: str, path: str | Path = "output/benchmarks.json"):
        self.query = query
        self.path = Path(path)
        self.tasks: list[dict] = []
        self.routing: list[dict] = []
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._t0 = self._last = time.perf_counter()

    def start(self) -> None:
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._t0 = self._last = time.perf_counter()

    def _route(self, event: str, **extra) -> None:
        entry = {"t": round(time.perf_counter() - self._t0, 3), "event": event}
        entry.update({k: v for k, v in extra.items() if v})
        self.routing.append(entry)

    def record_task(self, name: str, agent: str, seconds: float | None = None) -> None:
        now = time.perf_counter()
        seconds = now - self._last if seconds is None else seconds
        self._last = now
        self.tasks.append({"task": name, "agent": str(agent), "seconds": round(seconds, 3)})
        self._route("task_completed", task=name, agent=str(agent))

    # --- CrewAI callbacks ---
    def on_task(self, output) -> None:
        name = getattr(output, "name", None) or (getattr(output, "description", "") or "task")[:80]
        self.record_task(name, getattr(output, "agent", None) or "unknown")

    def on_step(self, step) -> None:
        tool = getattr(step, "tool", None)
        self._route("tool_call" if tool else "agent_step", tool=tool,
                    thought=(getattr(step, "thought", "") or "")[:120])

    @contextmanager
    def timed(self, name: str, agent: str):
        begin = time.perf_counter()
        self._route("task_started", task=name, agent=agent)
        try:
            yield
        finally:
            self.record_task(name, agent, seconds=time.perf_counter() - begin)

    def finish(self) -> dict:
        run = {
            "query": self.query,
            "started_at": self.started_at,
            "total_seconds": round(time.perf_counter() - self._t0, 3),
            "tasks": self.tasks,
            "routing_history": self.routing,
        }
        runs = []
        if self.path.exists():
            try:
                runs = json.loads(self.path.read_text()).get("runs", [])
            except (json.JSONDecodeError, AttributeError):
                runs = []
        runs.append(run)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"runs": runs}, indent=2))
        return run
