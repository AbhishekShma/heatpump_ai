"""Summary node - generates final summary after confirmation."""

from langchain_core.messages import AIMessage, SystemMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.summary_prompt import SUMMARY_PROMPT_TEMPLATE


def summary_node(state: State) -> dict:
    """Generate summary after user confirmation.
    
    Args:
        state: Current state containing messages history and questions.
        
    Returns:
        Dictionary with summary message and completion flag.
    """
    # Only run if user satisfied and conversation not yet complete
    if not state.all_questions_answered or not state.user_satisfied_with_responses or state.conversation_complete:
        return {}
    
    # Format prompt with questions
    prompt = SUMMARY_PROMPT_TEMPLATE.format(questions=state.questions)
    system_message = SystemMessage(content=prompt)
    
    # Combine system message with conversation history
    messages_with_system = [system_message] + state.messages
    
    # Invoke LLM
    result = llm.invoke(messages_with_system)
    
    # Add AI response to messages
    updated_messages = state.messages + [result]
    
    # Check for completion marker
    conversation_complete = False
    if result.content and "<SUMMARY_COMPLETE>true</SUMMARY_COMPLETE>" in result.content:
        conversation_complete = True
        # Remove the marker from the message content for cleaner output
        result.content = result.content.replace("<SUMMARY_COMPLETE>true</SUMMARY_COMPLETE>", "").strip()
    
    return {
        "messages": updated_messages,
        "conversation_complete": conversation_complete
    }
