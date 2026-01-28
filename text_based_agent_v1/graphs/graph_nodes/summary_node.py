"""Summary node placeholder."""
from __future__ import annotations

from graphs.schemas.state_schema import AgentState


def summary_node(state: AgentState) -> AgentState:
    """Provide a deterministic summary for the finalized phase."""

    answers = state.get("answers", {})
    if answers:
        lines = [
            f"- {answer.question_id} | {answer.question_text}: {answer.answer}"
            for answer in answers.values()
        ]
        body = "\n".join(lines)
    else:
        body = "No structured answers were captured before finalization."

    language = state.get("language", "de")
    if language == "de":
        content = f"Abschlusszusammenfassung:\n{body}"
    else:
        content = f"Final summary:\n{body}"

    return {
        "phase": "finalized",
        "message_history": [
            {
                "role": "assistant",
                "content": content,
            }
        ],
    }
