"""First message node - provides welcome message when no history exists."""

from langchain_core.messages import AIMessage

from graphs.schemas.state_schema import State
from components.prompts.welcome_message import WELCOME_MESSAGE


def greeting_node(state: State) -> dict:
    """Generate welcome message only if no messages exist.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Dictionary with welcome message if no history, empty dict otherwise.
    """
    # Only generate welcome message if:
    # 1. Messages list is completely empty
    # 2. Questions are provided (we're doing an assessment)
    if not state.questions or len(state.messages) > 0:
        return {}
    
    # No history - provide generic welcome message
    first_message = AIMessage(content=WELCOME_MESSAGE)
    return {"messages": [first_message]}

