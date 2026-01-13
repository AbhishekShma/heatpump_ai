"""Summary generation node for the summary generation agent."""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts import SUMMARY_GENERATION_PROMPT


def summary_node(state: State) -> dict:
    """Generate summary based on messages history and JSON data.
    
    Args:
        state: Current state containing messages history, conversation_data, and building_data.
        
    Returns:
        Dictionary with generated summary.
    """
    # Format messages as readable text
    messages_text = "\n".join([
        f"{'User' if msg.type == 'human' else 'AI'}: {msg.content}"
        for msg in state.messages
    ])
    
    # Format conversation_data (user responses and calculated values)
    conversation_data_text = json.dumps(state.conversation_data, indent=2) if state.conversation_data else "No conversation data provided"
    
    # Format building_data (building parameters)
    building_data_text = json.dumps(state.building_data, indent=2) if state.building_data else "No building data provided"
    
    # Create prompt with messages and both JSON structures
    prompt = SUMMARY_GENERATION_PROMPT.format(
        messages=messages_text,
        calculation_results=conversation_data_text,
        building_data=building_data_text
    )
    
    # Create messages for LLM
    llm_messages = [
        SystemMessage(content="You are a professional technical writer specializing in heat pump suitability assessments. Generate clear, professional summaries suitable for PDF documentation."),
        HumanMessage(content=prompt)
    ]
    
    # Generate summary
    result = llm.invoke(llm_messages)
    summary = result.content.strip()
    
    return {"summary": summary}
