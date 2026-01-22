"""Main entry point for subsidy calculation."""

from typing import Dict, List, Any
from graphs.main_graph import subsidy_graph
from graphs.schemas.state_schema import SubsidyState


def calculate_subsidies(
    questions_chat: Dict[str, Any],
    subsidy_table: Dict[str, Dict[str, Any]],
    recommended_heat_pump_list: List[Dict[str, Any]],
    stopping_criteria: str

) -> Dict[str, str]:
    """Calculate subsidies based on user responses, subsidy table, and recommended heat pumps.
    
    This function invokes a LangGraph that:
    1. Evaluates eligibility for each subsidy based on user responses
    2. Identifies model-dependent vs general subsidies
    3. Applies a 70% cap to total subsidies if needed
    4. Returns a plain text explanation of eligible subsidies
    
    Args:
        questions_chat: JSON dictionary containing user responses from chat interface.
        subsidy_table: Dictionary of subsidies keyed by subsidy ID. Each subsidy contains:
            - sub_id: Subsidy identifier
            - title: Subsidy title
            - description: Subsidy description (used to determine eligibility and model-dependency)
            - is_active: Whether the subsidy is currently active
            - created_at: Timestamp of creation
            - updated_at: Timestamp of last update
        recommended_heat_pump_list: List of recommended heat pumps with their details.
        
    Returns:
        Plain text string containing:
            - Explanation of each eligible subsidy
            - Total subsidy percentage (capped at 70% if applicable)
            - Message about 70% cap if applied
            - Message about model-dependent subsidies if applicable
            
    Example:
        >>> result = calculate_subsidies(
        ...     questions_chat={"income_level": "low", "home_age": "over_10_years"},
        ...     subsidy_table={
        ...         "1": {"sub_id": 1, "title": "Low Income Subsidy", "description": "...", "is_active": True, ...},
        ...         "2": {"sub_id": 2, "title": "Efficiency Bonus", "description": "...", "is_active": True, ...}
        ...     },
        ...     recommended_heat_pump_list=[{"id": "hp1", "name": "EcoHeat 3000", ...}]
        ... )
        >>> print(result)
        # Subsidy explanation text...
    """
    # Create initial state
    initial_state = SubsidyState(
        questions_chat=questions_chat,
        subsidy_table=subsidy_table,
        recommended_heat_pump_list=recommended_heat_pump_list,
        stopping_criteria=stopping_criteria
    )
    
    # Invoke the graph
    final_state = subsidy_graph.invoke(initial_state)
    
    # Return the evaluation results (plain text)
    return {"subsidy_calculation_evaluation_results": final_state.get("evaluation_results", "")}
