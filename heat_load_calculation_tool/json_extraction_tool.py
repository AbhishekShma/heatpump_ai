"""Tool for extracting JSON from conversation and storing it."""

import json
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import JSON_EXTRACTION_PROMPT

# Initialize LLM for JSON extraction
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract_and_store_json(summary: str, output_dir: str = "json_outputs") -> Dict[str, Any]:
    """
    Extract structured JSON from conversation summary and store it to a file.
    
    Args:
        summary: Conversation summary text containing building information
        output_dir: Directory to store JSON files (default: "json_outputs")
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating if extraction succeeded
            - json_data: Extracted JSON data (if successful)
            - file_path: Path to saved JSON file (if successful)
            - error: Error message (if failed)
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Extract JSON from summary
        prompt = JSON_EXTRACTION_PROMPT.format(summary=summary)
        
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
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"building_data_{timestamp}.json"
        file_path = output_path / filename
        
        # Save JSON to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "json_data": json_data,
            "file_path": str(file_path),
            "error": None
        }
        
    except json.JSONDecodeError as e:
        response_content = response.content if 'response' in locals() else 'No response'
        return {
            "success": False,
            "json_data": None,
            "file_path": None,
            "error": f"Failed to parse JSON: {str(e)}. Response was: {response_content}"
        }
    except Exception as e:
        return {
            "success": False,
            "json_data": None,
            "file_path": None,
            "error": f"Error extracting JSON: {str(e)}"
        }
