"""Main graph for the text-based agent."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import State
from graphs.graph_nodes.conversation_node import conversation_node

# Build the graph
builder = StateGraph(State)

# Add the single conversation node
builder.add_node("conversation", RunnableLambda(conversation_node))

# Set up edges: START -> conversation -> END
builder.add_edge(START, "conversation")
builder.add_edge("conversation", END)

# Compile the graph
main_graph = builder.compile()

