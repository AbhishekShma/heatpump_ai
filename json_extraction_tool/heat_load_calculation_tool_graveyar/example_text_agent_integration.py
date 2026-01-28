"""
Example: Integrating heat_load_calculation_tool with text-based agent

This shows how to add the calculation node to the text-based agent graph.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import State
from graphs.graph_nodes.greeting_node import greeting_node
from graphs.graph_nodes.conversation_node import conversation_node
from json_extraction_tool import heat_load_calculation_node

# Build the graph
builder = StateGraph(State)

# Add nodes
builder.add_node("greeting", RunnableLambda(greeting_node))
builder.add_node("conversation", RunnableLambda(conversation_node))
builder.add_node("calculate_heat_load", RunnableLambda(heat_load_calculation_node))

# Set up edges:
# START -> greeting -> conversation -> calculate_heat_load -> END
builder.add_edge(START, "greeting")
builder.add_edge("greeting", "conversation")
builder.add_edge("conversation", "calculate_heat_load")
builder.add_edge("calculate_heat_load", END)

# Compile the graph
main_graph = builder.compile()

# Usage example:
# from graphs.main_graph import main_graph
# result = main_graph.invoke({"messages": [HumanMessage(content="Hello")]})
