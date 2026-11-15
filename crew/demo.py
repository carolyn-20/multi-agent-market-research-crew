"""Offline demo: exercises tools, benchmarking and PDF output without any LLM or API key.
Uses ILLUSTRATIVE (invented) figures; it is for verifying the pipeline, not real research."""
from pathlib import Path

from .analysis import summary_markdown
from .benchmarks import BenchmarkLogger

SAMPLE_CSV = """company,revenue_busd,yoy_growth_pct,operating_margin_pct,rd_spend_busd,pe_ratio
Alpha Systems,52.1,11.4,31.2,7.8,28.5
Beta Cloud,38.4,18.9,24.7,6.1,35.2
Gamma Semis,27.9,-3.2,19.5,5.4,18.9
Delta Software,21.3,14.0,36.8,3.9,31.7
Epsilon Devices,64.7,6.5,22.1,9.2,22.4
Zeta Security,9.6,24.3,15.4,2.2,42.0
"""


def run_offline(query: str, out_dir: Path, bench: BenchmarkLogger) -> str:
    csv_path = out_dir / "metrics.csv"
    with bench.timed("Research", "Market Researcher (offline)"):
        csv_path.write_text(SAMPLE_CSV)
    with bench.timed("Analysis", "Financial Analyst (offline)"):
        table = summary_markdown(str(csv_path))
    with bench.timed("Writing", "Content Writer (offline)"):
        md = f"""# {query}

## Executive Summary
**Offline demo report.** This document was produced without an LLM or live data to verify the
PDF, benchmarking and Pandas pipeline. All figures are *illustrative*. Run `python main.py --query "..."`
with API keys for real research.

## Key Metrics
The sample dataset covers six fictional technology companies across revenue, growth, margin,
R&D spend and valuation. The statistical summary appears in the appendix.

## Analysis
- Revenue is widely dispersed, signalling a market led by a few scaled incumbents.
- Growth ranges from contraction to above 20%, with smaller firms growing fastest.
- Operating margins cluster in the 15-37% band; software-style models sit at the top.

## Risks and Outlook
Valuation multiples vary sharply, so earnings misses may be punished unevenly.

## Sources
Illustrative sample data bundled with the project (`crew/demo.py`).
"""
    return md
