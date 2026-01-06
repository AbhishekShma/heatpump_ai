"""Main graph for the text-based agent."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Local imports
from graphs.schemas.state_schema import State
from graphs.graph_nodes.greeting_node import greeting_node
from graphs.graph_nodes.conversation_node import conversation_node

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

