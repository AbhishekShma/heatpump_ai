"""Main graph for subsidy calculation using LangGraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import SubsidyState
from graphs.graph_nodes.subsidy_evaluator_node import subsidy_evaluator_node


# Build the graph
builder = StateGraph(SubsidyState)

# Add nodes
builder.add_node("subsidy_evaluator", RunnableLambda(subsidy_evaluator_node))

# Set up edges: Linear flow from START -> evaluator -> END
builder.add_edge(START, "subsidy_evaluator")
builder.add_edge("subsidy_evaluator", END)

# Compile the graph
subsidy_graph = builder.compile()
