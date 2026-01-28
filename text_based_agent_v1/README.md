# Text-Based Agent v1

A fresh implementation of the stateful conversational form engine described in `stateful_conversational_form_engine_design_overview.md`. This version focuses on explicit state management and a deterministic routing layer that activates individual conversation nodes based on state flags.

## Architecture Overview

- **Two-layer graph** powered by LangGraph
  - **Layer 1:** A dedicated `router` node that inspects the state (`phase`, `has_greeted`, etc.)
  - **Layer 2:** Four specialized nodes – `greeting`, `conversation`, `confirmation`, `summary`
- **State-first design:** All routing decisions and invariants derive from explicit state fields, never from implicit LLM memory.

language: Literal["en", "de"]
has_greeted: bool
## Core State Fields

```python
phase: Literal["asking", "confirming", "finalized"]
current_index: int
questions: List[Question]  # accepts the LiveKit metadata shape from agent_1
answers: Dict[str, Answer]  # mirrors the webhook payload from agent_1
pending_update_question_id: Optional[str]
language: Literal["en", "de"]
message_history: List[Dict[str, str]]
has_greeted: bool
conversation_id: int
```

`Question` understands the same fields that appear in `agent_1.py` (e.g.,
`text`, `description`, `is_mandatory`) so the metadata payload can be reused
verbatim. `Answer` replicates the webhook entry format (`question_id`,
`question_text`, `answer`, `conversation_id`) to make downstream integrations
drop-in compatible.

See `graphs/schemas/state_schema.py` for the authoritative definition, including helper models (`Question`, `Answer`) and aggregation helpers.

## Current Status

- High-level scaffolding is in place (state schema, router, placeholder nodes, graph wiring).
- Nodes currently emit simple placeholder messages so we can validate routing without invoking real tools.
- Future iterations will layer in:
  1. Question presentation + answer capture in the `conversation` node
  2. Update handling + `pending_update_question_id` logic
  3. Real confirmation + summary generation powered by LLMs and structured outputs

## Usage

```python
from text_based_agent_v1 import form_engine_graph, create_initial_state
from text_based_agent_v1.graphs.schemas.state_schema import Question

questions = [
    Question(id="q1", text="Which heating system do you use today?"),
    Question(id="q2", text="How large is your home in m²?"),
]
state = create_initial_state(questions=questions)

# Invoke router -> greeting
state = form_engine_graph.invoke(state)
# ... mutate state externally (e.g., phase transitions) and invoke again as needed
```

Run `example_usage.py` for a walkthrough that simulates the three phases manually.

## Requirements

Install dependencies from `requirements.txt` and set `OPENAI_API_KEY` in your environment if/when the nodes start calling the LLM.
