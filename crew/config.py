"""Environment-driven configuration. Secrets come from .env, never from code.

Default provider: Groq (OpenAI-compatible endpoint) with openai/gpt-oss-120b.
Override LLM_MODEL / LLM_BASE_URL / LLM_API_KEY in .env to use another provider.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))  # Groq counts this toward TPM
LLM_REASONING_EFFORT = os.getenv("LLM_REASONING_EFFORT", "low")  # low = fewer reasoning tokens
MAX_RPM = int(os.getenv("MAX_RPM", "6"))  # spread calls across the minute


def api_key() -> str | None:
    return os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")


def get_llm():
    """Single shared LLM for the manager and all workers."""
    from crewai import LLM

    return LLM(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=api_key(),
        temperature=0.2,
        max_tokens=LLM_MAX_TOKENS,
        reasoning_effort=LLM_REASONING_EFFORT,
    )


def output_dir() -> Path:
    """Resolve (and create) the output directory at call time so tests/CLI can override it."""
    path = Path(os.getenv("OUTPUT_DIR", "output"))
    path.mkdir(parents=True, exist_ok=True)
    return path
