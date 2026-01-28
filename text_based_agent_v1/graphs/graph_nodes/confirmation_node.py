"""Confirmation node placeholder."""
from __future__ import annotations

from graphs.schemas.state_schema import AgentState


def confirmation_node(state: AgentState) -> AgentState:
    """Request confirmation that collected answers are correct."""

    answers = state.get("answers", {})
    answered_ids = ", ".join(sorted(answers.keys())) or "noch keine / none"
    language = state.get("language", "de")

    if language == "de":
        content = (
            "Hier ist eine kurze Übersicht der bereits gespeicherten Antworten: "
            f"{answered_ids}. Bitte gib mir Bescheid, ob alles stimmt oder ob wir "
            "etwas korrigieren sollen."
        )
    else:
        content = (
            "Here is a quick overview of the answers on file: "
            f"{answered_ids}. Let me know if everything looks good or if you "
            "need to make a correction."
        )

    return {
        "message_history": [
            {
                "role": "assistant",
                "content": content,
            }
        ]
    }
