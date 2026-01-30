"""Greeting node placeholder."""
from __future__ import annotations

from graphs.schemas.state_schema import AgentState


def greeting_node(state: AgentState) -> AgentState:
    """Emit a deterministic greeting and flag that the user was welcomed."""

    question_count = len(state.get("questions", []))
    language = state.get("language", "de")
    if language == "de":
        content = (
            "Hallo! Ich helfe dir dabei, ein paar Fragen Schritt für Schritt zu beantworten."
            f" Insgesamt warten {question_count} Fragen auf dich."
        )
    else:
        content = (
            "Hi there! I'm ready to guide you through the upcoming questions one at a time."
            f" There are {question_count} questions in total."
        )

    return {"has_greeted": True,
        "message_history": [
            {
                "role": "assistant",
                "content": content,
            }
        ],
    }
