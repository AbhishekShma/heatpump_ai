"""Main graph for the text-based agent."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import State
from graphs.graph_nodes.greeting_node import greeting_node
from graphs.graph_nodes.conversation_node import conversation_node
from graphs.graph_nodes.confirmation_node import confirmation_node
from graphs.graph_nodes.summary_node import summary_node


def should_go_to_confirmation(state: State) -> str:
    """Route based on completion and satisfaction status."""
    if not state.all_questions_answered:
        return END
    
    # If user is satisfied, go to summary
    if state.user_satisfied_with_responses:
        return "summary"
    
    # Otherwise, go to confirmation (it will handle the loop)
    return "confirmation"


def route_after_confirmation(state: State) -> str:
    """Route after confirmation node."""
    # If user satisfied, go to summary
    if state.user_satisfied_with_responses:
        return "summary"
    
    # Check if confirmation was just requested (last message is AI asking for confirmation)
    from langchain_core.messages import AIMessage
    if state.messages:
        last_msg = state.messages[-1]
        if isinstance(last_msg, AIMessage) and last_msg.content:
            content_lower = last_msg.content.lower()
            # If last message is asking for confirmation, wait for user response
            if any(phrase in content_lower for phrase in [
                "confirm", "is everything correct", "would you like to change",
                "ist alles korrekt", "möchten sie etwas ändern"
            ]):
                return END  # Wait for user response
    
    # Otherwise, loop back to confirmation (user wants changes or handling response)
    return "confirmation"


# Build the graph
builder = StateGraph(State)

# Add nodes
builder.add_node("greeting", RunnableLambda(greeting_node))
builder.add_node("conversation", RunnableLambda(conversation_node))
builder.add_node("confirmation", RunnableLambda(confirmation_node))
builder.add_node("summary", RunnableLambda(summary_node))

# Set up edges
builder.add_edge(START, "greeting")
builder.add_edge("greeting", "conversation")


builder.add_conditional_edges(
    "conversation",
    should_go_to_confirmation,
    {
        "confirmation": "confirmation",
        "summary": "summary",
        END: END
    }
)
# Confirmation routes based on user satisfaction
builder.add_conditional_edges(
    "confirmation",
    route_after_confirmation,
    {
        "confirmation": "confirmation",  # Loop back if user wants changes
        "summary": "summary",  # Go to summary if satisfied
        END: END  # Wait for user response
    }
)
builder.add_edge("summary", END)

# Compile the graph
main_graph = builder.compile()

