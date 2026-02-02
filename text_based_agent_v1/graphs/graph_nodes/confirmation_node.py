"""Confirmation node placeholder."""
from __future__ import annotations

from typing import Any, Dict

from graphs.schemas.state_schema import AgentState


def confirmation_node(state: AgentState) -> Dict[str, Any]:
    """Request confirmation that collected answers are correct."""

    
    # answered_ids = ", ".join(sorted(answers.keys())) or "noch keine / none"
    # language = state.get("language", "de")
    """

    Tasks:
    1. Call llm with answers stored and ask for confirmation.
        
        IF Confirm:
        If confirm, call tool -> set phase to finalized.

        IF NOT Confirm:
        If not confirm, call update tool.
        In update tool , get question, answer Id, based on user message.
        Call tool to update question at correct index/id.
        feed back to llm which generates response based on value returned from the tool, which will indicate 
        success or failure of update.

    """
    answers = state.answers
    language = state.language

    # chat_history = state.messages
    confirmation_node_prompt = 

    
    return {}