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

_raw_model = (
    os.getenv("GROQ_MODEL")
    or os.getenv("MODEL_NAME")
    or "llama-3.3-70b-versatile"
)
if _raw_model.startswith("groq/"):
    _raw_model = _raw_model[len("groq/") :]
if _raw_model in {"llama3-8b-8192", "llama-3.1-8b-8192"}:
    _raw_model = "llama-3.1-8b-instant"
MODEL = _raw_model

BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
TEMPERATURE = float(os.getenv("JARVIS_TEMPERATURE", "0.3"))
MAX_ITER = int(os.getenv("JARVIS_MAX_ITER", "8"))
VERBOSE = os.getenv("JARVIS_VERBOSE", "true").lower() in {"1", "true", "yes"}

SKILLS_DIR = ROOT / "skills"
MEMORY_DIR = ROOT / "memory"
LOGS_DIR = ROOT / "logs"

for d in (SKILLS_DIR, MEMORY_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def require_api_key() -> str:
    if not API_KEY:
        raise RuntimeError(
            "Missing API key. Set GitHub secret 'groq_api_key' "
            "or env GROQ_API_KEY / groq_api_key.\n"
            "Example: groq_api_key=gsk_xxxxxxxx"
        )
    return API_KEY
