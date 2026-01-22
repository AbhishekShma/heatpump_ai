"""Subsidy evaluator node for the subsidy calculation graph."""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from graphs.schemas.state_schema import SubsidyState
from components.llm import llm
from components.prompts.subsidy_evaluation_prompt import SUBSIDY_EVALUATION_PROMPT


def subsidy_evaluator_node(state: SubsidyState) -> dict:
    """Evaluate subsidy eligibility and generate user-facing text explanation.
    
    This node uses an LLM to:
    1. Analyze each subsidy in the subsidy table
    2. Map subsidy requirements to user responses
    3. Determine eligibility for each subsidy
    4. Generate plain text explanation with capping logic
    
    Args:
        state: Current state containing questions_chat, subsidy_table, and recommended_heat_pump_list.
        
    Returns:
        Dictionary with evaluation_results containing plain text explanation.
    """
    # Format inputs for the prompt
    questions_chat_str = json.dumps(state.questions_chat, indent=2, ensure_ascii=False)
    subsidy_table_str = json.dumps(state.subsidy_table, indent=2, ensure_ascii=False)
    heat_pump_list_str = json.dumps(state.recommended_heat_pump_list, indent=2, ensure_ascii=False)
    
    # Format the prompt with inputs
    formatted_prompt = SUBSIDY_EVALUATION_PROMPT.format(
        questions_chat=questions_chat_str,
        subsidy_table=subsidy_table_str,
        recommended_heat_pump_list=heat_pump_list_str
    )
    
    # Create messages for LLM
    messages = [
        SystemMessage(content="You are an expert subsidy advisor. Provide clear, professional explanations in plain text."),
        HumanMessage(content=formatted_prompt)
    ]
    
    # Invoke LLM
    result = llm.invoke(messages)
    
    # Return plain text result
    return {
        "evaluation_results": result.content.strip()
    }
