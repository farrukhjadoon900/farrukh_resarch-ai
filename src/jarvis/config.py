"""Configuration — reads groq_api_key and optional overrides from env."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

API_KEY = (
    os.getenv("groq_api_key")
    or os.getenv("GROQ_API_KEY")
    or ""
)

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
TEMPERATURE = float(os.getenv("JARVIS_TEMPERATURE", "0.3"))
MAX_ITER = int(os.getenv("JARVIS_MAX_ITER", "12"))
VERBOSE = os.getenv("JARVIS_VERBOSE", "true").lower() in {"1", "true", "yes"}

SKILLS_DIR = ROOT / "skills"
MEMORY_DIR = ROOT / "memory"
LOGS_DIR = ROOT / "logs"

for d in (SKILLS_DIR, MEMORY_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def require_api_key() -> str:
    if not API_KEY:
        raise RuntimeError(
            "Missing API key. Set environment variable 'groq_api_key' "
            "(GitHub Secrets) or put it in .env\n"
            "Example: groq_api_key=gsk_xxxxxxxx"
        )
    return API_KEY
