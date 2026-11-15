"""Assemble the hierarchical crew (manager LLM + Researcher/Analyst/Writer)."""
from crewai import Crew, Process

from .agents import build_agents
from .benchmarks import BenchmarkLogger
from .config import LLM_MODEL, MAX_RPM, get_llm
from .tasks import build_tasks


def build_crew(query: str, bench: BenchmarkLogger) -> Crew:
    llm = get_llm()
    agents = build_agents(llm)
    print(f"[manager] Initialising hierarchical workflow with manager LLM '{LLM_MODEL}' "
          f"for query: {query!r}")
    return Crew(
        agents=list(agents.values()),
        tasks=build_tasks(query),
        process=Process.hierarchical,
        manager_llm=llm,
        max_rpm=MAX_RPM,
        step_callback=bench.on_step,
        task_callback=bench.on_task,
        verbose=True,
    )
