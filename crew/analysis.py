"""Pure-Pandas analysis helpers (no CrewAI dependency, so they are easy to test)."""
from __future__ import annotations

import pandas as pd


def summarize_csv(csv_path: str) -> pd.DataFrame:
    """Return count/mean/std/min/quartiles/max for every numeric column."""
    df = pd.read_csv(csv_path)
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("CSV contains no numeric columns to summarise.")
    return numeric.describe()


def summary_markdown(csv_path: str, decimals: int = 2) -> str:
    """Summary statistics rendered as a Markdown table."""
    return summarize_csv(csv_path).round(decimals).to_markdown()
