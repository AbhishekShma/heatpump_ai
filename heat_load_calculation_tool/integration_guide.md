# Integration Guide: Heat Load Calculation Tool

## For Text-Based Agent

### Method 1: As a LangChain Tool (Recommended)

This allows the LLM to automatically call the tool when it has gathered all necessary information.

#### Step 1: Update conversation_node.py

Modify your `conversation_node` to bind the tool to the LLM:

```python
from heat_load_calculation_tool import heat_load_calculation_tool_langchain
from langchain_core.messages import ToolMessage

def conversation_node(state: State) -> dict:
    # ... existing code ...
    
    # Bind tools to LLM
    from components.llm import llm
    llm_with_tools = llm.bind_tools([heat_load_calculation_tool_langchain])
    
    # Use llm_with_tools instead of llm
    result = llm_with_tools.invoke(messages_with_system)
    
    updated_messages = state.messages + [result]
    
    # Handle tool calls
    if hasattr(result, 'tool_calls') and result.tool_calls:
        for tool_call in result.tool_calls:
            if tool_call["name"] == "heat_load_calculation_tool_langchain":
                # Execute tool
                tool_result = heat_load_calculation_tool_langchain.invoke(tool_call["args"])
                
                # Add tool message
                tool_message = ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"]
                )
                updated_messages.append(tool_message)
                
                # Get LLM response to tool result
                final_messages = [system_message] + updated_messages
                final_result = llm_with_tools.invoke(final_messages)
                updated_messages.append(final_result)
    
    return {"messages": updated_messages}
```

#### Step 2: Update agent instructions

Add to your agent instructions that it should call the heat load calculation tool when all information is gathered:

```python
AGENT_INSTRUCTIONS_WITH_QUESTIONS = """
...
COMPLETION
- Once all questions are answered, use the heat_load_calculation_tool_langchain tool
  to calculate the heat load based on the gathered information
- After the tool returns results, present them to the user in a friendly, understandable way
...
"""
```

### Method 2: As a Graph Node

Add the calculation as a separate node in your graph:

```python
from heat_load_calculation_tool import heat_load_calculation_node
from langchain_core.runnables import RunnableLambda

builder.add_node("calculate_heat_load", RunnableLambda(heat_load_calculation_node))
builder.add_edge("conversation", "calculate_heat_load")
builder.add_edge("calculate_heat_load", END)
```

## For Voice Agent (agent_v3)

Simply add the tool to your agent:

```python
from heat_load_calculation_tool import heat_load_calculation_tool

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[heat_load_calculation_tool],
        )
```

The tool will be automatically available to the LLM and can be called when needed.
