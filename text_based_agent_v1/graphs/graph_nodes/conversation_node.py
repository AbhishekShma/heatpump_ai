"""Conversation node placeholder."""
from __future__ import annotations

from graphs.schemas.state_schema import AgentState
from typing import Dict, Any

def _format_question_prompt(question: Dict[str,Any], idx: int) -> str:
    """Mirror the phrasing style used in agent_1 when announcing questions."""

    question_text = question.get("question") or "no question found"
    prefix = "[MANDATORY] " if question.get("is_mandatory_for_cal") else ""
    return f"Question :{idx + 1}: {prefix}{question_text}".strip()


def conversation_node(state: AgentState) -> AgentState:
    """Surface the next question or acknowledge that asking is complete."""

    idx = state.get("current_index", 0)
    questions = state.get("questions", [])
    if idx < len(questions):
        question = questions[idx]
        content = _format_question_prompt(question, idx)
    else:
        content = (
            "All configured questions have already been asked. "
            "Set phase='confirming' to progress to the confirmation node."
        )

    return {
        "messages": [
            {
                "role": "assistant",
                "content": content,
            }
        ]
    }
