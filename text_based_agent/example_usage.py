"""Example usage of the text-based agent."""

from langchain_core.messages import HumanMessage, AIMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State


def main():
    """Example of how to use the text-based agent."""
    questions_str = """1. What is your house type? (detached, semi-detached, or apartment)
2. What year was your house built?
3. What is the approximate heated floor area in square meters?
4. What heating system do you currently use?"""
    
    print("=== Example: Full Conversation Starting with No History ===")
    
    # Start with no history - empty messages list
    messages = []
    
    # Step 1: AI provides welcome message (no user message yet)
    print("\n--- Turn 1: AI Welcome Message ---")
    state1 = State(messages=messages, questions=questions_str)
    result1 = main_graph.invoke(state1)
    messages = result1['messages']  # Update with AI welcome message
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 2: User answers first question
    print("--- Turn 2: Answer to Question 1 ---")
    user_msg_2 = HumanMessage(content="My house is detached")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_2]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_2)
    state2 = State(messages=messages, questions=questions_str)
    result2 = main_graph.invoke(state2)
    messages = result2['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 3: User goes off-topic
    print("--- Turn 3: Off-topic message ---")
    user_msg_3 = HumanMessage(content="By the way, what's the weather like today?")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_3]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_3)
    state3 = State(messages=messages, questions=questions_str)
    result3 = main_graph.invoke(state3)
    messages = result3['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 4: User answers second question
    print("--- Turn 4: Answer to Question 2 ---")
    user_msg_4 = HumanMessage(content="It was built in 1995")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_4]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_4)
    state4 = State(messages=messages, questions=questions_str)
    result4 = main_graph.invoke(state4)
    messages = result4['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 4.5: User requests English language
    print("--- Turn 4.5: Language Preference Request ---")
    user_msg_4_5 = HumanMessage(content="Sprechen Sie bitte auf Englisch")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_4_5]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_4_5)
    state4_5 = State(messages=messages, questions=questions_str)
    result4_5 = main_graph.invoke(state4_5)
    messages = result4_5['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 5: User answers third question
    print("--- Turn 5: Answer to Question 3 ---")
    user_msg_5 = HumanMessage(content="About 120 square meters")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_5]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_5)
    state5 = State(messages=messages, questions=questions_str)
    result5 = main_graph.invoke(state5)
    messages = result5['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 6: User goes off-topic again
    print("--- Turn 6: Another off-topic message ---")
    user_msg_6 = HumanMessage(content="Do you know any good restaurants nearby?")
    last_user_msg = next((msg for msg in reversed(messages + [user_msg_6]) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    messages.append(user_msg_6)
    state6 = State(messages=messages, questions=questions_str)
    result6 = main_graph.invoke(state6)
    messages = result6['messages']  # Update with AI response
    last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
    if last_ai_msg:
        print(f"AI: {last_ai_msg.content}\n")
    
    # Step 7: User answers fourth question (all questions answered)
    print("--- Turn 7: Answer to Question 4 (All Questions Answered) ---")
    user_msg_7 = HumanMessage(content="I currently use a gas boiler")
    messages.append(user_msg_7)
    last_user_msg = next((msg for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
    if last_user_msg:
        print(f"User: {last_user_msg.content}")
    state7 = State(messages=messages, questions=questions_str)
    result7 = main_graph.invoke(state7)
    messages = result7['messages']  # Update with AI response and summary
    # Print all AI messages (response and summary if present)
    for msg in messages[len(state7.messages):]:
        if isinstance(msg, AIMessage):
            print(f"AI: {msg.content}\n")
    
    # print("=== Full Conversation History ===")
    # print(f"Total messages: {len(messages)}\n")
    # for i, msg in enumerate(messages, 1):
    #     msg_type = "User" if isinstance(msg, HumanMessage) else "AI"
    #     print(f"{i}. {msg_type}: {msg.content}\n")


if __name__ == "__main__":
    main()

