"""Main graph for the summary generation agent."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import State
from graphs.graph_nodes.summary_node import summary_node

# Build the graph
builder = StateGraph(State)

# Add single node for summary generation
builder.add_node("summary", RunnableLambda(summary_node))

# Set up edges: START -> summary -> END
builder.add_edge(START, "summary")
builder.add_edge("summary", END)

# Compile the graph
main_graph = builder.compile()
