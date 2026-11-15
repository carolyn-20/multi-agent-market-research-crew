"""The three worker agents (short prompts on purpose: fewer tokens per call)."""
from crewai import Agent

from .config import get_llm
from .tools import calculate_financial_metrics, save_metrics_csv, web_scraper


def build_agents(llm=None) -> dict[str, Agent]:
    llm = llm or get_llm()
    common = dict(llm=llm, allow_delegation=False, verbose=True, max_iter=4)
    return {
        "researcher": Agent(role="Market Researcher",
                            goal="Find credible recent data on the topic.",
                            backstory="Equity researcher who extracts hard numbers.",
                            tools=[web_scraper, save_metrics_csv], **common),
        "analyst": Agent(role="Financial Analyst",
                         goal="Compute statistics and give concise insights.",
                         backstory="Quant analyst; reports only supported numbers.",
                         tools=[calculate_financial_metrics], **common),
        "writer": Agent(role="Content Writer",
                        goal="Write a concise Markdown market report.",
                        backstory="Business journalist.", **common),
    }
