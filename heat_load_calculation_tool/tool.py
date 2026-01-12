"""Main tool function for heat load calculation."""

from typing import Dict, Any, Optional
from .graph import calculation_graph
from .schemas import CalculationState


def calculate_heat_load_from_summary(summary: str) -> Dict[str, Any]:
    """
    Calculate heat load from conversation summary.
    
    This function uses a langgraph to:
    1. Extract structured JSON from the summary
    2. Call the heat load calculation function with the JSON
    
    Args:
        summary: Conversation summary text from the agent
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating if calculation succeeded
            - calculation_result: Heat load calculation results (if successful)
            - error: Error message (if failed)
            - json_data: Extracted JSON data (for debugging)
    """
    # Initialize state
    initial_state = CalculationState(summary=summary)
    
    # Run the graph
    result = calculation_graph.invoke(initial_state.model_dump())
    
    # Format response
    if result.get("error"):
        return {
            "success": False,
            "error": result["error"],
            "calculation_result": None,
            "json_data": result.get("json_data")
        }
    
    if result.get("calculation_result"):
        return {
            "success": True,
            "calculation_result": result["calculation_result"],
            "error": None,
            "json_data": result.get("json_data")
        }
    
    return {
        "success": False,
        "error": "Unknown error occurred",
        "calculation_result": None,
        "json_data": result.get("json_data")
    }
