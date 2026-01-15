"""First message node - provides welcome message when no history exists."""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.greeting_prompt import GREETING_PROMPT_TEMPLATE


def greeting_node(state: State) -> dict:
    """Generate dynamic welcome message using LLM, responding to user input if present.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with dynamically generated welcome message if no AI messages exist, empty dict otherwise.
    """
    # print(f"\n==============================Entered greeting node==============================\n")
    # Only generate welcome message if:
    # 1. Questions are provided (we're doing an assessment)
    # 2. No AI messages exist yet (first interaction)
    # 3. Questions are not yet answered (don't greet after completion)
    if not state.questions:
        return {}
    
    # Skip if questions are already answered or user is satisfied
    if state.all_questions_answered or state.user_satisfied_with_responses:
        return {}
    
    # Check if there's already an AI message (greeting already sent)
    has_ai_message = any(isinstance(msg, AIMessage) for msg in state.messages)
    if has_ai_message:
        return {}
    
    # Format greeting prompt with questions
    greeting_prompt = GREETING_PROMPT_TEMPLATE.format(questions=state.questions)
    
    # Prepare messages for LLM: system prompt + any existing user messages
    messages = [SystemMessage(content=greeting_prompt)]
    
    if state.messages:
        # Include any existing messages (user messages) so LLM can respond to them
        messages.extend(state.messages)
        # print(f"\n=============================\nMessages in greeting node=================\n {messages}\n=============================\n")
    
    # Generate dynamic greeting using LLM
    result = llm.invoke(messages)
    # print(f"\n=============================\nResult of LLM in greeting node\n===================\n {result}\n=============================\n")
    first_message = AIMessage(content=result.content)
    return {"messages": [first_message]}

