"""First message node - starts conversation with first question immediately."""

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from graphs.schemas.state_schema import State
from components.llm import llm
from components.prompts.conversation_prompt import (
    AGENT_INSTRUCTIONS_WITH_QUESTIONS,
    QUESTIONS_SECTION_TEMPLATE
)


def greeting_node(state: State) -> dict:
    """Generate first question if this is the first interaction.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with first question message if first interaction, empty dict otherwise.
    """
    # Only generate first question if:
    # 1. Messages list is completely empty (no user messages, no AI messages)
    # 2. Questions are provided (we're doing an assessment)
    if len(state.messages) > 0 or not state.questions:
        return {}
    
    # Extract first question - get the first line/numbered item
    first_question = state.questions.split('\n')[0] if '\n' in state.questions else state.questions.split('\\n')[0] if '\\n' in state.questions else state.questions
    
    # Remove leading number/bullet if present (e.g., "1. " or "1. ")
    first_question = first_question.lstrip('0123456789. ').strip()
    
    # Use the full instructions with questions section for consistency
    questions_section = QUESTIONS_SECTION_TEMPLATE.format(questions=state.questions)
    instructions = AGENT_INSTRUCTIONS_WITH_QUESTIONS.format(questions_section=questions_section)
    
    # Create a prompt that includes introduction and first question
    intro_prompt = """Start the conversation with:
1. A brief introduction: "Hello! I'm a heat pump recommendation assistant. I'll ask you a few questions to understand your needs and provide a personalized heat pump recommendation."
2. Then immediately ask the first question: {first_question}

Keep it concise - introduction should be 1-2 sentences, then go straight to the question.""".format(first_question=first_question)
    
    system_message = SystemMessage(content=instructions)
    user_message = HumanMessage(content=intro_prompt)
    
    messages = [system_message, user_message]
    result = llm.invoke(messages)
    
    # Add first question as AI message
    first_message = AIMessage(content=result.content)
    
    return {"messages": [first_message]}

