"""Assemble the hierarchical crew (manager LLM + Researcher/Analyst/Writer)."""
from crewai import Crew, Process

from .agents import build_agents
from .benchmarks import BenchmarkLogger
from .config import MANAGER_MODEL
from .tasks import build_tasks


def build_crew(query: str, bench: BenchmarkLogger) -> Crew:
    agents = build_agents()
    print(f"[manager] Initialising hierarchical workflow with manager LLM '{MANAGER_MODEL}' "
          f"for query: {query!r}")
    return Crew(
        agents=list(agents.values()),
        tasks=build_tasks(query),
        process=Process.hierarchical,
        manager_llm=MANAGER_MODEL,
        step_callback=bench.on_step,
        task_callback=bench.on_task,
        verbose=True,
    )
