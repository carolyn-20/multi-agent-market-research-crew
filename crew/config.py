"""Environment-driven configuration. Secrets come from .env, never from code.

Default provider: Groq (OpenAI-compatible endpoint) with openai/gpt-oss-120b.
Override LLM_MODEL / LLM_BASE_URL / LLM_API_KEY in .env to use another provider.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)  # .env wins over stale Windows/system variables

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))  # Groq counts this toward TPM
LLM_REASONING_EFFORT = os.getenv("LLM_REASONING_EFFORT", "low")  # low = fewer reasoning tokens
MAX_RPM = int(os.getenv("MAX_RPM", "6"))  # spread calls across the minute


def api_key() -> str | None:
    """Prefer an explicit key; for the Groq endpoint pick the first candidate that looks like a Groq key."""
    cands = [os.getenv(k, "").strip().strip('"\'') for k in ("LLM_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY")]
    cands = [c for c in cands if c]
    if "groq.com" in LLM_BASE_URL:
        for c in cands:
            if c.startswith("gsk_"):
                return c
    return cands[0] if cands else None


def validate_llm_api_key(key: str | None = None, base_url: str | None = None) -> str:
    """Return a usable API key or exit with a clear message."""
    key = key or api_key()
    base_url = base_url or LLM_BASE_URL
    if not key:
        raise SystemExit("No API key found. Set GROQ_API_KEY in .env, or use --offline.")
    if "groq.com" in base_url and not key.startswith("gsk_"):
        raise SystemExit(
            "API key does not look like a Groq key (Groq keys start with 'gsk_'). "
            "Fix GROQ_API_KEY in .env, or set LLM_BASE_URL for your provider. "
            "Use --offline to run without a live LLM."
        )
    return key


def build_llm(model: str):
    from crewai import LLM
    import os

    return LLM(
        model=model,
        provider="openai",
        base_url=LLM_BASE_URL,
        api_key=os.getenv("LLM_API_KEY"),
        max_tokens=LLM_MAX_TOKENS,
        reasoning_effort=LLM_REASONING_EFFORT,
    )


def get_llm():
    """Single shared LLM for the manager and all workers."""
    return build_llm(LLM_MODEL)


def output_dir() -> Path:
    """Resolve (and create) the output directory at call time so tests/CLI can override it."""
    path = Path(os.getenv("OUTPUT_DIR", "output"))
    path.mkdir(parents=True, exist_ok=True)
    return path