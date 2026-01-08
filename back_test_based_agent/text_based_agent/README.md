# Text-Based Agent

A LangGraph-based conversational agent with a single-node architecture.

## Structure

```
text_based_agent/
├── graphs/
│   ├── schemas/
│   │   └── state_schema.py      # State schema with messages history
│   ├── graph_nodes/
│   │   └── conversation_node.py # Single LLM conversation node
│   └── main_graph.py            # Main graph definition
├── components/
│   └── llm.py                   # LLM initialization
└── example_usage.py             # Example usage script
```

## Features

- **Single-node architecture**: Simple graph with one conversation node
- **Chat history**: Maintains conversation context using `messages` field in State
- **LangGraph-based**: Uses LangGraph for state management and graph execution

## Usage

```python
from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State

# Initialize with a user message
state = State(messages=[HumanMessage(content="Hello!")])

# Invoke the graph
result = main_graph.invoke(state)

# Get AI response
ai_response = result['messages'][-1].content
```

## Requirements

- langgraph
- langchain-core
- langchain-openai
- python-dotenv

Make sure to set your `OPENAI_API_KEY` in your `.env` file.

