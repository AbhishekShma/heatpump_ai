"""State schema for the summary generation agent graph."""

from typing import Annotated, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class State(BaseModel):
    """State schema for the summary generation agent.
    
    Attributes:
        messages: List of chat messages (history) containing the conversation.
        calculation_results: JSON data with user responses and calculated values (heat load, etc.).
        building_parameters: JSON data with building parameters (area, year, renovations, etc.).
        summary: Generated summary (output).
    """
    messages: Annotated[
        List[BaseMessage], 
        Field(description="Contains the chat history")
    ] = []
    
    calculation_results: Annotated[
        Optional[Dict[str, Any]],
        Field(description="JSON data with user responses and calculated values (heat load, transmission loss, etc.)", default=None)
    ] = None
    
    building_parameters: Annotated[
        Optional[Dict[str, Any]],
        Field(description="JSON data with building parameters (area, year, renovations, insulation, etc.)", default=None)
    ] = None
    
    summary: Annotated[
        str,
        Field(description="Generated summary based on messages and JSON data", default="")
    ] = ""
