"""Jarvis configuration — reads Google API key and runtime overrides from environment."""

from **future** import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ─────────────────────────────────────────────

# PROJECT ROOT

# ─────────────────────────────────────────────

ROOT = Path(**file**).resolve().parents[2]

# Load local .env if available.

# GitHub Actions environment variables override these values.

load_dotenv(ROOT / ".env")

# ─────────────────────────────────────────────

# API KEY

# ─────────────────────────────────────────────

API_KEY = (
os.getenv("GOOGLE_API_KEY")
or ""
)

# ─────────────────────────────────────────────

# MODEL

# ─────────────────────────────────────────────

MODEL = (
os.getenv("MY_MODEL")
or "gemini-flash-latest"
)

# ─────────────────────────────────────────────

# BASE URL

# ─────────────────────────────────────────────

BASE_URL = (
os.getenv("BASE_URL")
or "https://generativelanguage.googleapis.com/v1beta"
)

# ─────────────────────────────────────────────

# JARVIS SETTINGS

# ─────────────────────────────────────────────

try:
TEMPERATURE = float(
os.getenv("JARVIS_TEMPERATURE", "0.3")
)
except ValueError:
TEMPERATURE = 0.3

try:
MAX_ITER = int(
os.getenv("JARVIS_MAX_ITER", "8")
)
except ValueError:
MAX_ITER = 8

VERBOSE = (
os.getenv("JARVIS_VERBOSE", "true").lower()
in {"1", "true", "yes", "on"}
)

# ─────────────────────────────────────────────

# DIRECTORIES

# ─────────────────────────────────────────────

SKILLS_DIR = ROOT / "skills"
MEMORY_DIR = ROOT / "memory"
LOGS_DIR = ROOT / "logs"

for directory in (
SKILLS_DIR,
MEMORY_DIR,
LOGS_DIR,
):
directory.mkdir(
parents=True,
exist_ok=True,
)

# ─────────────────────────────────────────────

# API KEY VALIDATION

# ─────────────────────────────────────────────

def require_api_key() -> str:
"""
Return the configured Google API key.

```
The key is expected from the GitHub Actions
secret GOOGLE_API_KEY or local .env.
"""

if not API_KEY:
    raise RuntimeError(
        "Missing API key.\n\n"
        "Set GitHub Actions secret 'GOOGLE_API_KEY' "
        "or define GOOGLE_API_KEY in .env.\n"
        "Example: GOOGLE_API_KEY=AIzaSy..."
    )

return API_KEY

