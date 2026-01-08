"""Main graph for the text-based agent."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda


# Local imports
from app.text_based_agent.graphs.schemas.state_schema import State
from app.text_based_agent.graphs.graph_nodes.greeting_node import greeting_node
from app.text_based_agent.graphs.graph_nodes.conversation_node import conversation_node

# Build the graph
builder = StateGraph(State)

# Add nodes: greeting runs first, then conversation
builder.add_node("greeting", RunnableLambda(greeting_node))
builder.add_node("conversation", RunnableLambda(conversation_node))

# Set up edges: START -> greeting -> conversation -> END
builder.add_edge(START, "greeting")
builder.add_edge("greeting", "conversation")
builder.add_edge("conversation", END)

# Compile the graph
main_graph = builder.compile()

