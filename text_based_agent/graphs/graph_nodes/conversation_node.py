"""Conversation node for the text-based agent."""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.agent_instructions_with_questions_prompt import AGENT_INSTRUCTIONS_WITH_QUESTIONS
from components.prompts.questions_section_template_prompt import QUESTIONS_SECTION_TEMPLATE


def conversation_node(state: State) -> dict:
    """Process user message and generate AI response using chat history.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with updated messages including AI response.
    """
    # print(f"\n==============================Entered conversation node==============================\n")
    # Return empty if no messages
    if not state.messages:
        return {}
    
    # Skip if questions are already answered or user is satisfied
    if state.all_questions_answered or state.user_satisfied_with_responses or state.conversation_complete:
        return {}
    
    # Skip if last message is already an AI message (greeting was just added)
    # Only process if there's a user message waiting for a response
    if isinstance(state.messages[-1], AIMessage):
        # print(f"\n=============================\nLast message is already an AI message. Skipping conversation node.\n=============================\n")
        return {}
    
    # Format instructions with questions (questions are always required)
    questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
    instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    
    # Create system message with agent instructions
    system_message = SystemMessage(content=instructions)
    
    # Combine system message with full conversation history
    # The messages list already contains the full history (HumanMessage, AIMessage, etc.)
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM
    result = llm.invoke(messages_with_system)
    
    # Add AI response to messages
    updated_messages = state.messages + [result]
    
    # Check for completion marker
    completion_detected = False
    if result.content and "<COMPLETION>true</COMPLETION>" in result.content:
        completion_detected = True
        # Remove the marker from the message content for cleaner output
        result.content = result.content.replace("<COMPLETION>true</COMPLETION>", "").strip()
    
    # Set completion flag
    all_questions_answered = state.all_questions_answered or completion_detected

    return {
        "messages": updated_messages,
        "all_questions_answered": all_questions_answered
    }

