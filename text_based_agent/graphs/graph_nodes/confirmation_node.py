"""Confirmation node - seeks user confirmation before generating summary."""

from langchain_core.messages import AIMessage, SystemMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.confirmation_prompt import CONFIRMATION_PROMPT


def confirmation_node(state: State) -> dict:
    """Seek user confirmation when all questions are answered.
    
    Args:
        state: Current state containing messages history and questions.
        
    Returns:
        Dictionary with confirmation message and satisfaction flag.
    """
    # Only run if all questions answered and user not yet satisfied
    if not state.all_questions_answered or state.user_satisfied_with_responses or state.conversation_complete:
        return {}
    # Format prompt with questions
    prompt = CONFIRMATION_PROMPT.format(questions=state.questions, history=state.messages)
    system_message = SystemMessage(content=prompt)
    
    # Combine system message with conversation history
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM
    result = llm.invoke(messages_with_system)
    
    # Add AI response to messages
    updated_messages = state.messages + [result]
    
    # Check for confirmation marker
    user_satisfied = False
    if result.content and "<CONFIRMED_CONFIRMATION>true</CONFIRMED_CONFIRMATION>" in result.content:
        user_satisfied = True
        # Remove the marker from the message content for cleaner output
        result.content = result.content.replace("<CONFIRMED_CONFIRMATION>true</CONFIRMED_CONFIRMATION>", "").strip()
    
    return {
        "messages": updated_messages,
        "user_satisfied_with_responses": user_satisfied
    }
