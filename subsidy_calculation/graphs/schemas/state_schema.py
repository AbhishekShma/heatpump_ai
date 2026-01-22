"""State schema for the subsidy calculation graph."""

from typing import Annotated, Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SubsidyState(BaseModel):
    """State schema for subsidy calculation.
    
    Attributes:
        questions_chat: JSON containing user responses from chat interface.
        subsidy_table: Dictionary of subsidies (keyed by subsidy ID).
        recommended_heat_pump_list: List of recommended heat pumps.
        evaluation_results: Final subsidy explanation text with eligibility and capping information.
    """
    
    # Inputs
    questions_chat: Annotated[
        Dict[str, Any],
        Field(description="User responses from chat interface as JSON")
    ] = {}
    
    subsidy_table: Annotated[
        Dict[str, Dict[str, Any]],
        Field(description="Dictionary of subsidies keyed by subsidy ID")
    ] = {}
    
    recommended_heat_pump_list: Annotated[
        List[Dict[str, Any]],
        Field(description="List of recommended heat pumps")
    ] = []
    
    # Output
    evaluation_results: Annotated[
        Optional[str],
        Field(description="Final subsidy explanation text with eligibility and capping information")
    ] = None
