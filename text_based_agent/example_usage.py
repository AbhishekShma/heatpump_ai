"""Example usage of the text-based agent."""

from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State


def main():
    """Example of how to use the text-based agent."""
    questions_str = """1. What is your house type? (detached, semi-detached, or apartment)
2. What year was your house built?
3. What is the approximate heated floor area in square meters?
4. What heating system do you currently use?"""
    
    # Example 1: User starts with general conversation, agent redirects to questions
    print("=== Example 1: User Starts with General Conversation (Agent Redirects) ===")
    initial_state = State(
        messages=[HumanMessage(content="Hello! How are you?, can you tell me about polar bears?")],
        questions=questions_str
    )
    result = main_graph.invoke(initial_state)
    print(f"AI Response: {result['messages'][-1].content}\n")
    
    # Example 2: Empty messages with questions (first message node will initiate)
    print("=== Example 2: Empty Messages with Questions (First Question Initiated) ===")
    
    # Start with empty messages - greeting node will generate initial explanation
    state_empty_messages = State(
        messages=[],
        questions=questions_str
    )
    
    result_empty = main_graph.invoke(state_empty_messages)
    print(f"AI Response (Greeting): {result_empty['messages'][-1].content}\n")
    
    # Example 3: With questions to ask one by one (user initiated)
    print("=== Example 3: With Questions (User Initiated) ===")
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

