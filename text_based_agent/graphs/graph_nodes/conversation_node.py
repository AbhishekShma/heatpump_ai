"""Conversation node for the text-based agent."""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.conversation_prompt import (
    AGENT_INSTRUCTIONS_WITH_QUESTIONS,
    AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS,
    QUESTIONS_SECTION_TEMPLATE
)
from components.prompts.summary_prompt import SUMMARY_PROMPT_TEMPLATE
from graphs.graph_nodes.tool_handler import handle_tool_calls, get_tools


def conversation_node(state: State) -> dict:
    """Process user message and generate AI response using chat history.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with updated messages including AI response.
    """
    # Return empty if no messages
    if not state.messages:
        return {}
    
    # Skip if last message is already an AI message (greeting was just added)
    # Only process if there's a user message waiting for a response
    if isinstance(state.messages[-1], AIMessage):
        return {}
    
    # Format instructions based on whether questions are provided
    if state.questions:
        questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
        instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    else:
        instructions = AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS
    
    # Create system message with agent instructions
    system_message = SystemMessage(content=instructions)
    
    # Bind tools to LLM - enable JSON extraction tool
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # Combine system message with full conversation history
    # The messages list already contains the full history (HumanMessage, AIMessage, etc.)
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM with tools enabled
    result = llm_with_tools.invoke(messages_with_system)
    
    # Add AI response to messages (result is already an AIMessage with tool_calls if any)
    updated_messages = state.messages + [result]
    
    # Handle tool calls if any
    updated_messages = handle_tool_calls(result, updated_messages, system_message, llm_with_tools)
    
    # Check if all questions are answered and generate summary using LLM
    if state.questions:
        summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(questions=state.questions)
        summary_messages = [system_message] + updated_messages + [HumanMessage(content=summary_prompt)]
        summary_result = llm.invoke(summary_messages)
        
        # Only add summary if LLM generated content (empty means not all questions answered)
        if summary_result.content and summary_result.content.strip():
            summary_message = AIMessage(content=summary_result.content)
            updated_messages = updated_messages + [summary_message]
    
    return {"messages": updated_messages}

