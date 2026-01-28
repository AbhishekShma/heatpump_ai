"""Tool handler for the text-based agent."""

import sys
from pathlib import Path
from langchain_core.messages import ToolMessage

# Add parent directory to path to import json extraction tool
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from json_extraction_tool.heat_load_calculation_tool_graveyar.json_extraction_langchain_tool import json_extraction_tool_langchain


def get_tools():
    """
    Get list of tools available to the agent.
    
    Returns:
        List of tool instances
    """
    return [json_extraction_tool_langchain]


def handle_tool_calls(result, updated_messages, system_message, llm_with_tools):
    """
    Handle tool calls from LLM response.
    
    Args:
        result: AIMessage from LLM that may contain tool_calls
        updated_messages: Current list of messages
        system_message: System message for context
        llm_with_tools: LLM instance with tools bound
        
    Returns:
        Updated list of messages after handling tool calls
    """
    # Check if LLM wants to call a tool
    if hasattr(result, 'tool_calls') and result.tool_calls:
        for tool_call in result.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            if tool_name == "json_extraction_tool_langchain":
                # Extract summary from tool args
                summary = tool_args.get("summary", "")
                
                # Call the tool
                tool_result = json_extraction_tool_langchain.invoke({"summary": summary})
                
                # Add tool message to conversation
                tool_message = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call.get("id", "")
                )
                updated_messages.append(tool_message)
                
                # Get LLM response to tool result
                final_messages = [system_message] + updated_messages
                final_result = llm_with_tools.invoke(final_messages)
                updated_messages.append(final_result)
    
    return updated_messages
