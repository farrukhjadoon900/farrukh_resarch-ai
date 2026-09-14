"""Groq LLM factory for CrewAI — OpenAI-compatible endpoint."""

from __future__ import annotations

from crewai import LLM

from jarvis.config import API_KEY, BASE_URL, MODEL, TEMPERATURE, require_api_key


def get_llm(model: str | None = None, temperature: float | None = None) -> LLM:
    """Return a CrewAI LLM pointed at Groq Cloud."""
    require_api_key()
    return LLM(
        model=model or MODEL,
        base_url=BASE_URL,
        api_key=API_KEY,
        temperature=TEMPERATURE if temperature is None else temperature,
    )
