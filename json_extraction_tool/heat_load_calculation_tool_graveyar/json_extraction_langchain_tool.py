"""LangChain tool wrapper for text-based agent - JSON extraction only."""

from langchain_core.tools import tool
from ..json_extraction_tool import extract_and_store_json
import json


@tool
def json_extraction_tool_langchain(summary: str) -> str:
    """
    Extract building information from conversation summary and save it as JSON.
    
    This tool extracts structured building data from the conversation summary,
    creates a JSON file, and stores it for later use.
    
    Use this tool when you have gathered all the necessary information about a building
    (area, year built, postal code, renovation status, etc.) and want to save it as JSON.
    
    Args:
        summary: A summary of the conversation containing building information.
                Should include: area (m²), number of floors, construction year,
                postal code, renovation status, insulation status, etc.
    
    Returns:
        A formatted string indicating success or error message with file path.
    """
    result = extract_and_store_json(summary)
    
    if result["success"]:
        return f"""Successfully extracted and saved building data:

File saved to: {result['file_path']}
JSON data: {json.dumps(result['json_data'], indent=2)}"""
    else:
        return f"Error extracting JSON: {result['error']}"
