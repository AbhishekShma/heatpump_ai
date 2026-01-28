"""Schemas for the heat load calculation tool."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CalculationState(BaseModel):
    """State schema for the heat load calculation graph.
    
    Attributes:
        summary: The conversation summary text from the agent
        json_data: Extracted JSON data from the summary
        calculation_result: Result from the heat load calculation
        error: Any error that occurred during processing
    """
    summary: str = Field(description="Conversation summary from the agent")
    json_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extracted JSON data from summary"
    )
    calculation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Result from heat load calculation"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if processing failed"
    )
