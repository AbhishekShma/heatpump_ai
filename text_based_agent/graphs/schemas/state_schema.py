"""State schema for the text-based agent graph."""

from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class State(BaseModel):
    """State schema for the conversation agent.
    
    Attributes:
        messages: List of chat messages (history) containing the conversation.
        questions: Optional list of questions to ask the user one by one.
        all_questions_answered: Flag indicating if all questions have been answered.
    """
    messages: Annotated[
        List[BaseMessage], 
        Field(description="Contains the chat history")
    ] = []
    
    questions: Annotated[
        Optional[str],
        Field(description="Questions to ask the user (as a string, typically from JSON)")
    ] = None
    
    all_questions_answered: Annotated[
        bool,
        Field(description="Flag indicating if all questions have been answered", default=False)
    ] = False
    
    user_satisfied_with_responses: Annotated[
        bool,
        Field(description="Flag indicating if user is satisfied with their responses", default=False)
    ] = False
    
    conversation_complete: Annotated[
        bool,
        Field(description="Flag indicating if conversation is complete (summary generated)", default=False)
    ] = False

