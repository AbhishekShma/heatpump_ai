"""State schema for the text-based agent graph."""

from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class State(BaseModel):
    """State schema for the conversation agent.
    
    Attributes:
        messages: List of chat messages (history) containing the conversation.
        questions: Optional list of questions to ask the user one by one.
    """
    messages: Annotated[
        List[BaseMessage], 
        Field(description="Contains the chat history")
    ] = []
    
    questions: Annotated[
        Optional[str],
        Field(description="Questions to ask the user (as a string, typically from JSON)")
    ] = None

