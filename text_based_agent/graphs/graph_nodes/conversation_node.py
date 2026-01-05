"""Conversation node for the text-based agent."""

from langchain_core.messages import AIMessage, SystemMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.conversation_prompt import AGENT_INSTRUCTIONS_TEMPLATE, QUESTIONS_SECTION_TEMPLATE


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
    
    # Format instructions with questions if provided
    if state.questions:
        questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
        instructions = AGENT_INSTRUCTIONS_TEMPLATE.format(questions_section=questions_section)
    else:
        instructions = AGENT_INSTRUCTIONS_TEMPLATE.format(questions_section="")
    
    # Create system message with agent instructions
    system_message = SystemMessage(content=instructions)
    
    # Combine system message with full conversation history
    # The messages list already contains the full history (HumanMessage, AIMessage, etc.)
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM with the full conversation history including system instructions
    result = llm.invoke(messages_with_system)
    
    # Add AI response to messages
    ai_message = AIMessage(content=result.content)
    updated_messages = state.messages + [ai_message]
    
    return {"messages": updated_messages}

