"""Tasks carry no fixed agent: the manager LLM assigns them dynamically."""
from crewai import Task


def build_tasks(query: str) -> list[Task]:
    research = Task(
        name="Research",
        description=(
            f"Research: '{query}'. Use the web search tool to gather recent facts, news and "
            "company metrics. Then call 'Save Metrics CSV' with a CSV (snake_case header, one "
            "company or entity per row, numeric cells only, no units/symbols) containing at least "
            "4 numeric metrics for 5+ entities. Only use figures found in sources."),
        expected_output="Bullet-point findings with source URLs, plus the saved metrics CSV path.",
    )
    analysis = Task(
        name="Analysis",
        description=(
            "Run 'Financial Metrics Calculator' on the CSV path from the research task. "
            "Interpret the mean, min, max and standard deviation: highlight outliers, spread "
            "and what the numbers imply for the topic."),
        expected_output="The Markdown statistics table plus 4-6 analytical insights.",
        context=[research],
    )
    writing = Task(
        name="Writing",
        description=(
            f"Write the final report for '{query}' in Markdown. Use '# Title', then sections "
            "'## Executive Summary', '## Market Overview', '## Key Metrics', '## Analysis', "
            "'## Risks and Outlook', '## Sources'. Use only facts from the research/analysis."),
        expected_output="A complete Markdown report of roughly 600-900 words.",
        context=[research, analysis],
    )
    return [research, analysis, writing]
