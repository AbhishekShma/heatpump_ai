"""Conversation node for the text-based agent."""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from app.text_based_agent.graphs.schemas.state_schema import State
from app.text_based_agent.components.llm import llm
from app.text_based_agent.components.prompts.conversation_prompt import (
    AGENT_INSTRUCTIONS_WITH_QUESTIONS,
    AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS,
    QUESTIONS_SECTION_TEMPLATE
)
from app.text_based_agent.components.prompts.summary_prompt import SUMMARY_PROMPT_TEMPLATE


def conversation_node(state: State) -> dict:
    """Process user message and generate AI response using chat history.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with updated messages including AI response.
    """
    # Special case: If there are no messages and we have questions, generate welcome + first question
    if not state.messages and state.questions:
        # Generate welcome + first question together in one message
        pass  # Continue to process
    # Return empty if no messages and no questions
    elif not state.messages:
        return {}
    # Skip if last message is already an AI message (wait for user response)
    elif isinstance(state.messages[-1], AIMessage):
        return {}
    
    # Format instructions based on whether questions are provided
    if state.questions:
        questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
        instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    else:
        instructions = AGENT_INSTRUCTIONS_WITHOUT_QUESTIONS
    
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
    
    # Check if all questions are answered and generate summary using LLM
    # Count user messages (answers) and AI messages (questions)
    user_message_count = sum(1 for msg in state.messages if isinstance(msg, HumanMessage))
    ai_message_count = sum(1 for msg in state.messages if isinstance(msg, AIMessage))
    
    # Count how many questions are in the list (rough estimate based on numbering)
    # Questions are formatted as "1. Question text\n2. Question text\n..."
    question_count = state.questions.count('\n') + 1 if state.questions else 0
    
    # Only run summary check if:
    # 1. We have EXACTLY as many user answers as there are questions (all questions answered)
    # 2. We have at least as many AI messages as questions (all questions asked)
    # 3. This ensures we don't generate summary prematurely
    should_check_summary = (
        state.questions and 
        question_count > 0 and
        user_message_count == question_count and  # Exact match - all questions answered
        ai_message_count >= question_count  # All questions have been asked
    )
    
    if should_check_summary:
        summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(questions=state.questions)
        summary_messages = [system_message] + updated_messages + [HumanMessage(content=summary_prompt)]
        summary_result = llm.invoke(summary_messages)
        
        # Only add summary if LLM generated content (empty means not all questions answered)
        # Also check that the content is actually a complete summary
        if summary_result.content and summary_result.content.strip():
            content_lower = summary_result.content.lower()
            # Check if it's a complete summary (not partial)
            # Reject if it contains "awaiting" or "not answered" which indicates incomplete
            has_incomplete_indicators = any(phrase in content_lower for phrase in [
                "awaiting", "not answered", "not provided", "missing", "need to know"
            ])
            
            # Only add if it looks like a complete summary (contains summary words AND no incomplete indicators)
            if (any(word in content_lower for word in ["summary", "gathered", "information", "responses", "answers", "thank you"]) and
                not has_incomplete_indicators):
                summary_message = AIMessage(content=summary_result.content)
                updated_messages = updated_messages + [summary_message]
    
    return {"messages": updated_messages}

