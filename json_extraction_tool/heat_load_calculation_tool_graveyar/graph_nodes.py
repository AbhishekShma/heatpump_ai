"""Graph nodes for the heat load calculation tool."""

import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from .schemas import CalculationState
from .prompts import JSON_EXTRACTION_PROMPT

# Initialize LLM for JSON extraction
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract_json_node(state: CalculationState) -> Dict[str, Any]:
    """Extract structured JSON from conversation summary.
    
    Args:
        state: Current state containing the summary
        
    Returns:
        Dictionary with extracted json_data or error
    """
    try:
        # Create prompt for JSON extraction
        prompt = JSON_EXTRACTION_PROMPT.format(summary=state.summary)
        
        # Call LLM to extract JSON
        messages = [
            SystemMessage(content="You are a helpful assistant that extracts structured data from text and returns only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        json_str = response.content.strip()
        
        # Remove markdown code blocks if present
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()
        
        # Parse JSON
        json_data = json.loads(json_str)
        
        return {"json_data": json_data, "error": None}
        
    except json.JSONDecodeError as e:
        response_content = response.content if 'response' in locals() else 'No response'
        return {
            "json_data": None,
            "error": f"Failed to parse JSON: {str(e)}. Response was: {response_content}"
        }
    except Exception as e:
        return {
            "json_data": None,
            "error": f"Error extracting JSON: {str(e)}"
        }


def calculate_node(state: CalculationState) -> Dict[str, Any]:
    """Calculate heat load using extracted JSON data.
    
    Args:
        state: Current state containing json_data
        
    Returns:
        Dictionary with calculation_result or error
    """
    import os
    from dotenv import load_dotenv
    from calculation_functions.heat_load_wrapper import calculate_heat_load_from_json
    import tempfile
    
    if state.json_data is None:
        return {
            "calculation_result": None,
            "error": "No JSON data available for calculation"
        }
    
    try:
        # Load database URL from environment
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            return {
                "calculation_result": None,
                "error": "DATABASE_URL not found in environment variables"
            }
        
        # Write JSON to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(state.json_data, f, indent=2)
            json_path = f.name
        
        try:
            # Call calculation function
            result = calculate_heat_load_from_json(json_path, database_url)
            
            return {
                "calculation_result": result,
                "error": None
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(json_path)
            except:
                pass
                
    except Exception as e:
        return {
            "calculation_result": None,
            "error": f"Error calculating heat load: {str(e)}"
        }
