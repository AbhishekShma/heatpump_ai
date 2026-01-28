# Heat Load Calculation Tool

This tool extracts building information from conversation summaries, creates structured JSON, and calculates heat load using the building parameters.

## Architecture

The tool uses a **langgraph** with two nodes:
1. **extract_json_node**: Uses LLM to extract structured JSON from conversation summary
2. **calculate_node**: Calls the heat load calculation function with the extracted JSON

## Usage

### For Voice Agent (agent_v3)

Import and add the function tool to your agent:

```python
from heat_load_calculation_tool import heat_load_calculation_tool

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[heat_load_calculation_tool],  # Add the tool here
        )
```

The tool will be automatically available to the LLM. When the agent generates a summary, it can call this tool with the summary text.

### For Text-Based Agent

**Option 1: As a Tool (Recommended)**
Bind the tool to the LLM so it can be called automatically:

```python
from heat_load_calculation_tool import heat_load_calculation_tool_langchain
from components.llm import llm

# Bind tool to LLM
llm_with_tools = llm.bind_tools([heat_load_calculation_tool_langchain])

# Use llm_with_tools instead of llm in your conversation_node
# The LLM will automatically call the tool when it has gathered all information
```

**Option 2: As a Node**
Add the calculation node to your graph after the summary is generated:

```python
from heat_load_calculation_tool import heat_load_calculation_node
from langchain_core.runnables import RunnableLambda

# In your graph builder:
builder.add_node("calculate_heat_load", RunnableLambda(heat_load_calculation_node))

# Add edge from conversation node (where summary is generated) to calculation node
builder.add_edge("conversation", "calculate_heat_load")
builder.add_edge("calculate_heat_load", END)
```

## Configuration

The tool requires:
- `DATABASE_URL` environment variable (PostgreSQL connection string)
- OpenAI API key for JSON extraction (uses `gpt-4o-mini`)

Make sure these are set in your `.env` file.

## Input Format

The tool expects a conversation summary text that contains information about:
- Building area (m²)
- Number of floors
- Construction year
- Postal code
- Renovation status (optional)
- Insulation status (optional)
- Other building parameters (optional)

## Output Format

Returns a dictionary with:
- `success`: Boolean indicating if calculation succeeded
- `calculation_result`: Dictionary containing:
  - `heat_load`: Total heat load (W)
  - `H_t`: Transmission heat transfer coefficient (W/K)
  - `H_v`: Ventilation heat transfer coefficient (W/K)
  - `Dt`: Temperature difference (K)
- `error`: Error message (if failed)
- `json_data`: Extracted JSON data (for debugging)
