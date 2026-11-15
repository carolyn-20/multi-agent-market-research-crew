# Multi-Agent Market Research & Report Generator (CrewAI)

- **Repository**: [Insert URL]

A CrewAI project in which a **manager LLM** (`Process.hierarchical`) dynamically delegates work to a
**Researcher**, an **Analyst** and a **Writer**, then compiles the result into a typeset A4 PDF.

```
main.py                 CLI entry point
crew/
  config.py             env/config (models, output dir)
  tools.py              @tool: web scraper (Tavily/Serper), metrics CSV saver, Pandas financial parser
  analysis.py           pure-Pandas stats (mean/min/max/std...) -> Markdown
  agents.py / tasks.py  Researcher, Analyst, Writer + their tasks (no fixed agent: manager assigns)
  crew.py               hierarchical Crew with manager_llm
  benchmarks.py         per-task timings + routing trace -> benchmarks.json
  pdf_report.py         ReportLab: banner, styled sections, Pandas grid, "Page X of Y" footer
  demo.py               offline demo data (illustrative only)
tests/                  pytest suite
sample_outputs/         sample market_report.md / .pdf / metrics.csv / benchmarks.json
```

## Installation

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Configure keys: `cp .env.example .env`, then set `GROQ_API_KEY` and `TAVILY_API_KEY`
   (or `SERPER_API_KEY` as a fallback search provider). `.env` is git-ignored.
4. Run the app: `python main.py --query 'Tech Sector Q3 Analysis'`
5. Run tests: `pytest`

Outputs go to `output/` (override with `--output-dir` or `OUTPUT_DIR`):
`market_report.md`, `market_report.pdf`, `metrics.csv`, `benchmarks.json`.

### Offline demo (no API keys)
`python main.py --query 'Tech Sector Q3 Analysis' --offline` runs tools, benchmarking and PDF
generation on bundled **illustrative, invented** data. It bypasses the LLM crew, so it does not
satisfy Test Case 1; `sample_outputs/` was produced this way.

## How it maps to the verification cases

| Case | How to check |
|---|---|
| 1. Hierarchical execution | Run the command above. Console shows `[manager] Initialising hierarchical workflow...`, then CrewAI verbose logs showing delegation to the Researcher (search/CSV tools), Analyst (metrics calculator) and Writer. |
| 2. Data aggregation & PDF | `output/market_report.pdf`: header banner, Pandas statistics grid, "Page X of Y" footer. |
| 3. Automated tests | `pytest` (Pandas math, PDF layout/pagination, tools, benchmark log). |

## Benchmarks
`benchmarks.json` appends one run per execution: `tasks` (agent + seconds per task, measured between
completions) and `routing_history` (tool calls, agent steps and task completions with timestamps).

## Notes
- Tasks are deliberately created without an assigned agent so the manager LLM routes them.
- LLM: Groq `openai/gpt-oss-120b` for manager and workers (one shared `LLM`, see `crew/config.py`).
  Override `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY` in `.env` to use another provider.
- Token savers (Groq free tier = 8,000 tokens/min): `reasoning_effort=low`, `max_tokens=1500`
  (Groq counts it toward the per-minute budget), `max_rpm=6`, short prompts, one search, and
  scraper output capped at ~3,000 characters. Tune via `.env`.
- Tested against CrewAI 1.15 (crew construction) and with pytest both with and without CrewAI installed.
  The live LLM run needs your own API keys and was not executed here.
