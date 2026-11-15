"""Tasks carry no fixed agent: the manager LLM assigns them dynamically.
Descriptions and outputs are deliberately short to keep context (tokens) small."""
from crewai import Task


def build_tasks(query: str) -> list[Task]:
    research = Task(
        name="Research",
        description=(
            f"Research '{query}' with the web search tool (one search is enough). Then call "
            "'Save Metrics CSV' with a CSV: snake_case header, 5 companies, 4 numeric metrics, "
            "numbers only. Use only figures found in sources; if sources lack numbers, say so "
            "instead of inventing them."),
        expected_output="Max 120 words: 4 findings with source URLs, and the saved CSV path.",
    )
    analysis = Task(
        name="Analysis",
        description=("Run 'Financial Metrics Calculator' on the CSV path from the research. "
                     "Interpret mean, min, max and std."),
        expected_output="The Markdown table plus 3 insights, max 100 words of commentary.",
        context=[research],
    )
    writing = Task(
        name="Writing",
        description=(f"Write the report for '{query}' in Markdown: '# Title', then "
                     "'## Executive Summary', '## Key Metrics', '## Analysis', "
                     "'## Risks and Outlook', '## Sources'. Use only given facts."),
        expected_output="Markdown report, 350-450 words.",
        context=[research, analysis],
    )
    return [research, analysis, writing]
