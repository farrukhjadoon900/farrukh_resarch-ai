"""Gemini LLM factory for CrewAI — OpenAI-compatible endpoint."""

from **future** import annotations

from crewai import LLM

from jarvis.config import (
API_KEY,
BASE_URL,
MODEL,
TEMPERATURE,
require_api_key,
)

def get_llm(
model: str | None = None,
temperature: float | None = None,
) -> LLM:
"""Return a CrewAI LLM configured for the Google Gemini API."""


require_api_key()

selected_model = model or MODEL

# Remove provider prefix if MY_MODEL is configured as:
# gemini/xxx
if selected_model.startswith("gemini/"):
    selected_model = selected_model[len("gemini/"):]

return LLM(
    model=selected_model,
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=(
        TEMPERATURE
        if temperature is None
        else temperature
    ),
)

