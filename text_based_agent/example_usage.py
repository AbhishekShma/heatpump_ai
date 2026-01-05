"""Example usage of the text-based agent."""

from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State


def main():
    """Example of how to use the text-based agent."""
    # Example 1: General conversation without questions
    print("=== Example 1: General Conversation ===")
    initial_state = State(messages=[HumanMessage(content="Hello! How are you?")])
    result = main_graph.invoke(initial_state)
    print(f"AI Response: {result['messages'][-1].content}\n")
    
    # Example 2: With questions to ask one by one
    print("=== Example 2: With Questions ===")
    # Questions as a string (typically read from JSON)
    questions_str = """1. What is your house type? (detached, semi-detached, or apartment)
2. What year was your house built?
3. What is the approximate heated floor area in square meters?
4. What heating system do you currently use?"""
    
    state_with_questions = State(
        messages=[HumanMessage(content="I'd like to assess my heat pump suitability")],
        questions=questions_str
    )
    
    result2 = main_graph.invoke(state_with_questions)
    print(f"AI Response: {result2['messages'][-1].content}\n")
    
    # Continue conversation - questions are maintained in state
    next_state = State(
        messages=result2['messages'] + [HumanMessage(content="My house is detached")],
        questions=questions_str  # Questions persist across turns
    )
    result3 = main_graph.invoke(next_state)
    print(f"AI Response: {result3['messages'][-1].content}")


if __name__ == "__main__":
    main()

