"""Centralized LLM initialization for future use.

Even though the current nodes only emit placeholder messages, wiring up the LLM
here makes it trivial to plug it into the graph once we implement the real
conversation/summary logic.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def _build_llm() -> ChatOpenAI:
    """Create the default chat model instance.

    Returns:
        ChatOpenAI: Deterministic chat model configured via environment
            variables. Defaults to `gpt-4o-mini` for cost/performance balance.
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
    return ChatOpenAI(model=model, temperature=temperature)


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Return a cached LLM instance to avoid repeated auth handshakes."""
    return _build_llm()
