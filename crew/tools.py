"""Custom CrewAI tools: web search+scrape, metrics CSV writer, Pandas financial parser."""
from __future__ import annotations

import os
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .analysis import summary_markdown
from .config import output_dir

try:  # current CrewAI
    from crewai.tools import tool
except ImportError:  # older releases, as shown in the project brief
    try:
        from crewai_tools import tool
    except ImportError:  # allow tests to run without CrewAI installed
        def tool(arg):
            return arg if callable(arg) else (lambda fn: fn)

REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; MarketResearchCrew/1.0)"


# ----------------------------- search & scrape ----------------------------- #
def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Query Tavily (preferred) or SerperDev. Returns [{title, url, snippet}]."""
    tavily, serper = os.getenv("TAVILY_API_KEY"), os.getenv("SERPER_API_KEY")
    if tavily:
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": tavily, "query": query, "max_results": max_results},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return [
            {"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("content", "")}
            for x in r.json().get("results", [])
        ]
    if serper:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": serper, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return [
            {"title": x.get("title", ""), "url": x.get("link", ""), "snippet": x.get("snippet", "")}
            for x in r.json().get("organic", [])[:max_results]
        ]
    raise RuntimeError("Set TAVILY_API_KEY or SERPER_API_KEY in your .env file.")


def extract_text(html: str, max_chars: int = 3000) -> str:
    """Strip scripts/styles/nav and collapse whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars]


def scrape_url(url: str, max_chars: int = 3000) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return extract_text(resp.text, max_chars)


def search_and_scrape(query: str, max_results: int = 4) -> str:
    blocks = []
    for hit in search_web(query, max_results):
        try:
            body = scrape_url(hit["url"])
        except Exception:  # fall back to the search snippet if the page can't be fetched
            body = hit["snippet"]
        blocks.append(f"### {hit['title']}\nURL: {hit['url']}\n{body}")
    return "\n\n".join(blocks) or "No results found."


@tool("Web Search and Scrape")
def web_scraper(query: str) -> str:
    """Search the web for the query and return the scraped raw text of the top results."""
    try:
        return search_and_scrape(query)
    except Exception as exc:
        return f"Search failed: {exc}"


# ------------------------------- data tools -------------------------------- #
def write_metrics_csv(csv_text: str) -> str:
    """Validate CSV text with Pandas and save it to <output>/metrics.csv."""
    df = pd.read_csv(StringIO(csv_text.strip()))
    if df.select_dtypes(include="number").empty:
        raise ValueError("CSV needs at least one numeric column.")
    path = output_dir() / "metrics.csv"
    df.to_csv(path, index=False)
    return str(path)


@tool("Save Metrics CSV")
def save_metrics_csv(csv_text: str) -> str:
    """Save extracted metrics as CSV text (header row, one entity per row, numeric cells
    without units or symbols). Returns the file path to hand to the analyst."""
    try:
        return write_metrics_csv(csv_text)
    except Exception as exc:
        return f"Could not save CSV: {exc}"


@tool("Financial Metrics Calculator")
def calculate_financial_metrics(csv_path: str) -> str:
    """Loads corporate metrics from CSV and returns summary statistics as Markdown."""
    try:
        return summary_markdown(csv_path)
    except Exception as exc:
        return f"Could not analyse '{csv_path}': {exc}"
