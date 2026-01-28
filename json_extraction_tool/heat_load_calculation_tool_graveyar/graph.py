"""Langgraph for heat load calculation tool."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda

from .schemas import CalculationState
from .graph_nodes import extract_json_node, calculate_node

# Build the graph
builder = StateGraph(CalculationState)

# Add nodes
builder.add_node("extract_json", RunnableLambda(extract_json_node))
builder.add_node("calculate", RunnableLambda(calculate_node))

# Set up edges: START -> extract_json -> calculate -> END
builder.add_edge(START, "extract_json")
builder.add_edge("extract_json", "calculate")
builder.add_edge("calculate", END)

# Compile the graph
calculation_graph = builder.compile()
