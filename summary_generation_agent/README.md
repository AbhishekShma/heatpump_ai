# Summary Generation Agent

A LangGraph-based agent that generates summaries from conversation history and JSON data.

## Structure

```
summary_generation_agent/
├── graphs/
│   ├── schemas/
│   │   └── state_schema.py      # State schema with messages, json_data, and summary
│   ├── graph_nodes/
│   │   └── summary_node.py      # Single summary generation node
│   └── main_graph.py            # Main graph definition
├── components/
│   ├── llm.py                   # LLM initialization
│   └── prompts.py               # Summary generation prompts
└── example_usage.py             # Example usage script
```

## Features

- **Single-node architecture**: Simple graph with one summary generation node
- **Dual input**: Takes both conversation messages (history) and JSON data
- **Context-aware**: Combines information from messages and JSON to generate comprehensive summaries
- **LangGraph-based**: Uses LangGraph for state management and graph execution

## Usage

```python
from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State

# Prepare inputs
messages = [HumanMessage(content="My house was built in 1995")]
json_data = {"year": 1995, "area": 100.0}

# Create state
state = State(messages=messages, json_data=json_data)

# Invoke the graph
result = main_graph.invoke(state)

# Get generated summary
summary = result['summary']
```

## Requirements

- langgraph
- langchain-core
- langchain-openai
- pydantic
- python-dotenv

Make sure to set your `OPENAI_API_KEY` in your `.env` file.
