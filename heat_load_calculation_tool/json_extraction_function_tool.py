"""Function tool wrapper for voice agent - JSON extraction only."""

from typing import Optional
from livekit.agents import function_tool, RunContext
import json

from .json_extraction_tool import extract_and_store_json


@function_tool()
async def json_extraction_tool(
    context: RunContext,
    summary: str,
) -> str:
    """
    Extract building information from conversation summary and save it as JSON.
    
    This tool extracts structured building data from the conversation summary,
    creates a JSON file, and stores it for later use.
    
    Args:
        summary: A summary of the conversation containing building information
                (area, year built, postal code, renovation status, etc.)
    
    Returns:
        A formatted string indicating success or error message.
    """
    result = extract_and_store_json(summary)
    
    if result["success"]:
        return f"""Successfully extracted and saved building data:

File saved to: {result['file_path']}
JSON data: {json.dumps(result['json_data'], indent=2)}"""
    else:
        return f"Error extracting JSON: {result['error']}"
