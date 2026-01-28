"""Two-layer LangGraph wiring for the v1 agent."""
from __future__ import annotations

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

from graphs.graph_nodes.confirmation_node import confirmation_node
from graphs.graph_nodes.conversation_node import conversation_node
from graphs.graph_nodes.greeting_node import greeting_node
from graphs.graph_nodes.router_node import determine_route, router_node
from graphs.graph_nodes.summary_node import summary_node
from graphs.schemas.state_schema import AgentState

builder = StateGraph(AgentState)

builder.add_node("router", RunnableLambda(router_node))
builder.add_node("greeting", RunnableLambda(greeting_node))
builder.add_node("conversation", RunnableLambda(conversation_node))
builder.add_node("confirmation", RunnableLambda(confirmation_node))
builder.add_node("summary", RunnableLambda(summary_node))

builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    determine_route,
    {
        "greeting": "greeting",
        "conversation": "conversation",
        "confirmation": "confirmation",
        "summary": "summary",
    },
)

for terminal_node in ("greeting", "conversation", "confirmation", "summary"):
    builder.add_edge(terminal_node, END)

form_engine_graph = builder.compile()
