"""Node wrapper for text-based agent compatibility."""

from typing import Dict, Any
from langchain_core.messages import AIMessage

from ..tool import calculate_heat_load_from_summary


def heat_load_calculation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for text-based agent that calculates heat load from summary.
    
    This function extracts the summary from the last AI message (which should be
    the summary message) and calculates the heat load.
    
    Args:
        state: State dictionary containing messages list
        
    Returns:
        Dictionary with updated messages including calculation result
    """
    messages = state.get("messages", [])
    
    if not messages:
        return {}
    
    # Find the last AI message (should be the summary)
    summary_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            summary_message = msg
            break
    
    if not summary_message or not summary_message.content:
        return {}
    
    # Calculate heat load from summary
    result = calculate_heat_load_from_summary(summary_message.content)
    
    # Create response message
    if result["success"]:
        calc_result = result["calculation_result"]
        response_text = f"""Heat Load Calculation Results:

Total Heat Load: {calc_result['heat_load']:.2f} W
Transmission Heat Transfer Coefficient (H_t): {calc_result['H_t']:.2f} W/K
Ventilation Heat Transfer Coefficient (H_v): {calc_result['H_v']:.2f} W/K
Temperature Difference (Δt): {calc_result['Dt']:.2f} K"""
    else:
        response_text = f"Error calculating heat load: {result['error']}"
    
    # Add calculation result as new AI message
    result_message = AIMessage(content=response_text)
    updated_messages = messages + [result_message]
    
    return {"messages": updated_messages}
