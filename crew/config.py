"""Environment-driven configuration. Secrets come from .env, never from code."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MANAGER_MODEL = os.getenv("MANAGER_MODEL", "gpt-4o")
WORKER_MODEL = os.getenv("WORKER_MODEL", "gpt-4o-mini")


def output_dir() -> Path:
    """Resolve (and create) the output directory at call time so tests/CLI can override it."""
    path = Path(os.getenv("OUTPUT_DIR", "output"))
    path.mkdir(parents=True, exist_ok=True)
    return path
