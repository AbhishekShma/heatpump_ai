"""First message node - provides welcome message when no history exists."""

from langchain_core.messages import AIMessage

from app.text_based_agent.graphs.schemas.state_schema import State
from app.text_based_agent.components.prompts.welcome_message import WELCOME_MESSAGE


def greeting_node(state: State) -> dict:
    """Generate welcome message only if no messages exist.
    
    NOTE: For text-to-text chat, we skip the greeting and let conversation_node
    generate the welcome + first question together in one message.
    
    Args:
        state: Current state containing messages history and optional questions string.
        
    Returns:
        Empty dict (greeting will be included in conversation_node's first response).
    """
    # Skip greeting - conversation_node will generate welcome + first question together
    return {}

