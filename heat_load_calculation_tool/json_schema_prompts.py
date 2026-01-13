"""Prompts for extracting JSON using a schema/format file."""

import json
from pathlib import Path
from typing import Dict, Any


def load_json_schema(schema_path: str) -> Dict[str, Any]:
    """
    Load JSON schema/format file.
    
    Args:
        schema_path: Path to JSON file containing the desired format
        
    Returns:
        Dictionary containing the schema/format structure
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is not valid JSON
    """
    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_json_extraction_prompt_with_schema(
    summary: str, 
    schema_path: str,
    schema_description: str = None
) -> str:
    """
    Create a JSON extraction prompt that uses a JSON schema file.
    
    Args:
        summary: Conversation summary text containing building information
        schema_path: Path to JSON file containing the desired output format
        schema_description: Optional description of what the schema represents
        
    Returns:
        Formatted prompt string for JSON extraction
    """
    # Load the schema
    schema = load_json_schema(schema_path)
    schema_json_str = json.dumps(schema, indent=2)
    
    # Create description if not provided
    if schema_description is None:
        schema_description = "the following JSON structure"
    
    prompt = f"""You are a helpful assistant that extracts structured data from conversation summaries.

Given a conversation summary, extract the information and return it as valid JSON matching {schema_description}.

TARGET JSON FORMAT (use this as a template):
{schema_json_str}

EXTRACTION INSTRUCTIONS:
1. ALWAYS include ALL fields present in the target format above
2. For fields with example values in the schema:
   - Extract actual values from the summary when explicitly mentioned
   - Use the example values as defaults when not mentioned in the summary
3. Maintain the exact structure, nesting, and data types shown in the schema
4. For boolean fields: extract true/false based on summary content, use false as default if not mentioned
5. For numeric fields: extract actual numbers from summary, use schema example values as defaults
6. For nested objects: preserve the structure exactly as shown in the schema
7. For optional fields (like window_replacement_year): only include if mentioned in the summary
8. Return ONLY valid JSON matching the exact structure above, no additional text, markdown, or explanation
9. Ensure all numeric values use appropriate types (integers for counts/years, floats for measurements/temperatures)

Conversation Summary:
{summary}

Extract and return the JSON data matching the target format:"""
    
    return prompt


JSON_EXTRACTION_PROMPT_WITH_SCHEMA = """You are a helpful assistant that extracts structured data from conversation summaries.

Given a conversation summary and a JSON schema/format file, extract the information and return it as valid JSON matching the provided schema.

TARGET JSON FORMAT:
{schema_json}

EXTRACTION RULES:
1. ALWAYS include ALL fields present in the target format schema
2. Extract actual values from the summary when explicitly mentioned
3. For fields not mentioned in the summary:
   - Use the example values from the schema as defaults
   - For boolean fields, default to false unless context suggests otherwise
   - For numeric fields, use the schema example values as defaults
4. Maintain the exact structure, nesting, and data types shown in the schema
5. For nested objects (like "renovations"), preserve the complete structure with all keys
6. For optional fields, only include if mentioned in the summary or if they have default values in the schema
7. Return ONLY valid JSON matching the exact structure above, no additional text, markdown code blocks, or explanation
8. Ensure all numeric values use appropriate types (integers for counts/years, floats for measurements/temperatures)

Conversation Summary:
{summary}

Extract and return the JSON data matching the target format:"""
