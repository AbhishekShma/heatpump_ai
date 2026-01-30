"""Minimal walkthrough of the two-layer routing graph.

This script intentionally mutates the state between graph invocations to mimic how
an external orchestrator (LLM interpreter, UI layer, etc.) would drive the state
machine.
"""
from __future__ import annotations

# from text_based_agent_v1 import create_initial_state, form_engine_graph
from graphs.schemas.state_schema import Question
from graphs.main_graph import form_engine_graph
from graphs.schemas.state_schema import create_initial_state
def print_last_message(step_label: str, state) -> None:
    """Pretty-print the last assistant message for the demo."""

    history = state["message_history"]
    if not history:
        print(f"[{step_label}] <no messages recorded>")
        return

    last_entry = history[-1]
    print(f"[{step_label}] {last_entry['role']}: {last_entry['content']}")


if __name__ == "__main__":
    demo_questions = [
        Question(id="q1", text="Wie groß ist die Wohnfläche?", is_mandatory=True),
        Question(
            id="q2",
            text="Welche Heizungsart nutzt du aktuell?",
            metadata={"source": "agent_1_sample"},
        ),
    ]
    state = create_initial_state(questions=demo_questions, language="de")

    # 1) Router -> Greeting
    state = form_engine_graph.invoke(state)
    print_last_message("greeting", state)

    # 2) Router -> Conversation (still phase="asking")
    state = form_engine_graph.invoke(state)
    print_last_message("conversation", state)

    # Pretend we collected all answers and move to confirming
    state["phase"] = "confirming"

    # 3) Router -> Confirmation
    state = form_engine_graph.invoke(state)
    print_last_message("confirmation", state)

    # Pretend the user confirmed everything
    state["phase"] = "finalized"

    # 4) Router -> Summary (terminal)
    state = form_engine_graph.invoke(state)
    print_last_message("summary", state)

x = form_engine_graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
        f.write(x)