"""Routing node that fans out into the second-layer nodes."""
from __future__ import annotations

from typing import Literal

from graphs.schemas.state_schema import AgentState, Phase

RouteName = Literal["greeting", "conversation", "confirmation", "summary"]


def router_node(state: AgentState) -> AgentState:
    """Router is a pure inspection step so it returns an empty delta."""

    return {}


def determine_route(state: AgentState) -> RouteName:
    """Return the name of the node that should run next."""

    if not state.get("has_greeted", False):
        return "greeting"

    phase: Phase = state.get("phase", "asking")  # type: ignore[assignment]
    if phase == "asking":
        return "conversation"
    if phase == "confirming":
        return "confirmation"
    if phase == "finalized":
        return "summary"

    raise ValueError(f"Unsupported phase value: {phase}")
