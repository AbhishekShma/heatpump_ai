"""Function tool wrapper for voice agent compatibility."""

from typing import Optional
from livekit.agents import function_tool, RunContext

from .tool import calculate_heat_load_from_summary


@function_tool()
async def heat_load_calculation_tool(
    context: RunContext,
    summary: str,
) -> str:
    """
    Calculate heat load from a conversation summary about a building.
    
    This tool extracts building information from the summary, creates structured JSON,
    and calculates the heat load using the building parameters.
    
    Args:
        summary: A summary of the conversation containing building information
                (area, year built, postal code, renovation status, etc.)
    
    Returns:
        A formatted string containing the heat load calculation results or error message.
    """
    result = calculate_heat_load_from_summary(summary)
    
    if result["success"]:
        calc_result = result["calculation_result"]
        return f"""Heat Load Calculation Results:

Total Heat Load: {calc_result['heat_load']:.2f} W
Transmission Heat Transfer Coefficient (H_t): {calc_result['H_t']:.2f} W/K
Ventilation Heat Transfer Coefficient (H_v): {calc_result['H_v']:.2f} W/K
Temperature Difference (Δt): {calc_result['Dt']:.2f} K"""
    else:
        return f"Error calculating heat load: {result['error']}"
