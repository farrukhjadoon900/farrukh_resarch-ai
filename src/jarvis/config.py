from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ─────────────────────────────────────────────

# PROJECT ROOT

# ─────────────────────────────────────────────

ROOT = Path(**file**).resolve().parents[2]

load_dotenv(ROOT / ".env")

# ─────────────────────────────────────────────

# API KEY

# ─────────────────────────────────────────────

API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

# ─────────────────────────────────────────────

# MODEL

# ─────────────────────────────────────────────

MODEL = (
os.getenv("MY_MODEL")
or "gemini-flash-latest"
).strip()

# ─────────────────────────────────────────────

# BASE URL

# ─────────────────────────────────────────────

BASE_URL = (
os.getenv("BASE_URL")
or "https://generativelanguage.googleapis.com/v1beta"
).strip()

# ─────────────────────────────────────────────

# JARVIS SETTINGS

# ─────────────────────────────────────────────

try:
TEMPERATURE = float(
os.getenv("JARVIS_TEMPERATURE", "0.3")
)
except (TypeError, ValueError):
TEMPERATURE = 0.3

try:
MAX_ITER = int(
os.getenv("JARVIS_MAX_ITER", "8")
)
except (TypeError, ValueError):
MAX_ITER = 8

VERBOSE = (
os.getenv("JARVIS_VERBOSE", "true").strip().lower()
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
"""Return the configured Google API key."""


if not API_KEY:
    raise RuntimeError(
        "Missing API key. Set GitHub secret "
        "'GOOGLE_API_KEY' or environment variable "
        "GOOGLE_API_KEY.\n"
        "Example: GOOGLE_API_KEY=AIzaSyxxxxxxxx"
    )

return API_KEY

