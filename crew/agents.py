"""The three worker agents. Delegation is handled by the hierarchical manager."""
from crewai import Agent

from .config import WORKER_MODEL
from .tools import calculate_financial_metrics, save_metrics_csv, web_scraper


def build_agents() -> dict[str, Agent]:
    researcher = Agent(
        role="Market Researcher",
        goal="Find current, credible data and news about the requested market topic.",
        backstory="A veteran equity researcher who cross-checks sources and extracts hard numbers.",
        tools=[web_scraper, save_metrics_csv],
        llm=WORKER_MODEL, allow_delegation=False, verbose=True,
    )
    analyst = Agent(
        role="Financial Analyst",
        goal="Turn the collected metrics into verified statistics and clear insights.",
        backstory="A quantitative analyst who never reports a number the data does not support.",
        tools=[calculate_financial_metrics],
        llm=WORKER_MODEL, allow_delegation=False, verbose=True,
    )
    writer = Agent(
        role="Content Writer",
        goal="Write a polished, well-structured market report in Markdown.",
        backstory="A business journalist who writes crisp executive-ready reports.",
        llm=WORKER_MODEL, allow_delegation=False, verbose=True,
    )
    return {"researcher": researcher, "analyst": analyst, "writer": writer}
