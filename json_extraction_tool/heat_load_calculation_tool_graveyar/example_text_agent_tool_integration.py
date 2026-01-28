"""
Example: Integrating heat_load_calculation_tool as a tool (not node) for text-based agent

This shows how to bind the tool to the LLM so it can be called by the agent.
"""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from json_extraction_tool import heat_load_calculation_tool_langchain
from components.llm import llm


def conversation_node_with_tool(state):
    """Process user message with tool support.
    
    The LLM can call the heat_load_calculation_tool when it has gathered
    all the necessary information.
    """
    from graphs.schemas.state_schema import State
    from components.prompts.conversation_prompt import (
        AGENT_INSTRUCTIONS_WITH_QUESTIONS,
        AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS,
        QUESTIONS_SECTION_TEMPLATE
    )
    
    # Return empty if no messages
    if not state.messages:
        return {}
    
    # Skip if last message is already an AI message
    if isinstance(state.messages[-1], AIMessage):
        return {}
    
    # Format instructions
    if state.questions:
        questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
        instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    else:
        instructions = AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS
    
    # Create system message
    system_message = SystemMessage(content=instructions)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools([heat_load_calculation_tool_langchain])
    
    # Combine system message with conversation history
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM with tools
    result = llm_with_tools.invoke(messages_with_system)
    
    # Add AI response to messages
    updated_messages = state.messages + [result]
    
    # Check if LLM wants to call a tool
    if result.tool_calls:
        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name == "heat_load_calculation_tool_langchain":
                # Call the tool
                tool_result = heat_load_calculation_tool_langchain.invoke(tool_args)
                
                # Add tool message to conversation
                tool_message = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"]
                )
                updated_messages.append(tool_message)
                
                # Get LLM response to tool result
                final_messages = [system_message] + updated_messages
                final_result = llm_with_tools.invoke(final_messages)
                updated_messages.append(final_result)
    
    return {"messages": updated_messages}


# Alternative: Simpler version that handles tool calls automatically
def conversation_node_with_tool_auto(state):
    """Process user message with automatic tool execution."""
    from graphs.schemas.state_schema import State
    from components.prompts.conversation_prompt import (
        AGENT_INSTRUCTIONS_WITH_QUESTIONS,
        AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS,
        QUESTIONS_SECTION_TEMPLATE
    )
    from langchain_core.runnables import RunnableLambda
    
    # Return empty if no messages
    if not state.messages:
        return {}
    
    # Skip if last message is already an AI message
    if isinstance(state.messages[-1], AIMessage):
        return {}
    
    # Format instructions
    if state.questions:
        questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
        instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    else:
        instructions = AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS
    
    # Create system message
    system_message = SystemMessage(content=instructions)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools([heat_load_calculation_tool_langchain])
    
    # Create tool executor
    tools = [heat_load_calculation_tool_langchain]
    tool_map = {tool.name: tool for tool in tools}
    
    def execute_tool_calls(messages):
        """Execute tool calls and return updated messages."""
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                if tool_name in tool_map:
                    tool_result = tool_map[tool_name].invoke(tool_args)
                    tool_message = ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                    messages.append(tool_message)
        
        return messages
    
    # Combine system message with conversation history
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM with tools
    result = llm_with_tools.invoke(messages_with_system)
    updated_messages = state.messages + [result]
    
    # Execute tool calls if any
    updated_messages = execute_tool_calls(updated_messages)
    
    # If tools were called, get final LLM response
    if any(isinstance(msg, ToolMessage) for msg in updated_messages[-3:]):
        final_messages = [system_message] + updated_messages
        final_result = llm_with_tools.invoke(final_messages)
        updated_messages.append(final_result)
    
    return {"messages": updated_messages}
