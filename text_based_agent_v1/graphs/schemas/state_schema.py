"""State models for the v1 conversational form engine."""
from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional
from langchain_core.messages import BaseMessage

from pydantic import BaseModel, Field


Phase = Literal["asking", "confirming", "finalized","greeting"]
Language = Literal["en", "de"]


class AgentState(BaseModel):
    """Authoritative state for the deterministic form engine."""
    messages: Annotated[
        List[BaseMessage], 
        Field(description="Contains the chat history")
    ]
    phase: Annotated[
        Phase, 
        Field(description="Current phase of the form engine")
        ]
    current_index: Annotated[
        int, 
        Field(description="Index of the current question being asked")]
    questions: Annotated[
        List[Dict[str, Any]], 
        Field(description="List of questions to be asked")
        ]
    answers: Annotated[
        Dict[str, Any], 
        Field(description="Answers to the questions")
        ]
    pending_update_question_id: Annotated[
        Optional[str], 
        Field(description="ID of the question pending update")
        ]
    language: Annotated[
        Language, 
        Field(description="Contains language the agent is to communicate in")
        ]
    
    conversation_id: Annotated[
        str,
        Field(description="Unique identifier for the conversation")
    ]
    # message_history: Annotated[List[MessageEntry], append_message_history]
    # has_greeted: bool



# def create_initial_state(
#     *,
#     questions: Optional[List[Question]] = None,
#     language: Language = "de",
#     phase: Phase = "asking",
# ) -> AgentState:
#     """Helper factory used by tests and example scripts."""

#     return {
#         "phase": phase,
#         "current_index": 0,
#         "questions": questions or [],
#         "answers": {},
#         "pending_update_question_id": None,
#         "language": language,
#         "message_history": [],
#         "has_greeted": False,
#             "conversation_id": 1,
#     }

# Phase = Literal["asking", "confirming", "finalized"]
# Language = Literal["en", "de"]


# class Question(BaseModel):
#     """Data model mirroring the question payload emitted by agent_1."""

#     id: str = Field(description="Stable identifier used as the answers key")
#     text: Optional[str] = Field(
#         default=None,
#         description="Primary prompt shown to the user (matches 'text' in metadata)",
#     )
#     description: Optional[str] = Field(
#         default=None,
#         description="Fallback prompt used by some question payloads",
#     )
#     is_mandatory: bool = Field(
#         default=False,
#         description="Whether the question must be answered before advancing",
#     )
#     required: bool = Field(
#         default=True,
#         description="Back-compat flag; treated the same as `is_mandatory`",
#     )
#     metadata: Dict[str, Any] = Field(
#         default_factory=dict,
#         description="Arbitrary extra fields carried alongside each question",
#     )

#     @property
#     def prompt(self) -> str:
#         """Return whichever human-readable string should be spoken."""

#         return (self.text or self.description or "").strip()


# class Answer(BaseModel):
#     """Stores the normalized answer for a question (mirrors agent_1 payload)."""

#     question_id: str = Field(description="ID of the question that was answered")
#     question_text: str = Field(description="Snapshot of the question text when asked")
#     answer: str = Field(description="User provided response")
#     conversation_id: Optional[int] = Field(
#         default=None,
#         description="Sequence number used for audit trails/webhook payloads",
#     )


MessageEntry = Dict[str, str]


# def append_message_history(
#     existing: Optional[List[MessageEntry]],
#     updates: Optional[List[MessageEntry]],
# ) -> List[MessageEntry]:
#     """Accumulator for `message_history`.

#     LangGraph merges partial node outputs using these helper callbacks. The
#     router-plus-node architecture means most turns will append to the running
#     history rather than overwrite it.
#     """

#     if not existing and not updates:
#         return []
#     base = list(existing or [])
#     if updates:
#         base.extend(updates)
#     return base


# def merge_answer_store(
#     existing: Optional[Dict[str, Answer]],
#     updates: Optional[Dict[str, Answer]],
# ) -> Dict[str, Answer]:
#     """Merge answers by key, ensuring updates override previous entries."""

#     merged: Dict[str, Answer] = {}
#     if existing:
#         for question_id, answer in existing.items():
#             merged[question_id] = Answer.model_validate(answer)
#     if updates:
#         for question_id, answer in updates.items():
#             merged[question_id] = Answer.model_validate(answer)
#     return merged

