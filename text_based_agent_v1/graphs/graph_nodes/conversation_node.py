"""Conversation node placeholder."""
from __future__ import annotations

from graphs.schemas.state_schema import AgentState, Question


def _format_question_prompt(question: Question, idx: int) -> str:
    """Mirror the phrasing style used in agent_1 when announcing questions."""

    label = question.prompt or "(kein Text / missing text)"
    prefix = "[MANDATORY] " if question.is_mandatory or question.required else ""
    return f"Frage {idx + 1}: {prefix}{label}".strip()


def conversation_node(state: AgentState) -> AgentState:
    """Surface the next question or acknowledge that asking is complete."""

    idx = state.get("current_index", 0)
    questions = state.get("questions", [])
    if idx < len(questions):
        question: Question = questions[idx]
        content = _format_question_prompt(question, idx)
    else:
        content = (
            "All configured questions have already been asked. "
            "Set phase='confirming' to progress to the confirmation node."
        )

    return {
        "message_history": [
            {
                "role": "assistant",
                "content": content,
            }
        ]
    }
