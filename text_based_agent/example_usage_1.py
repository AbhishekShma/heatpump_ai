"""Example usage and tests for the text-based agent."""

import json
import os
from datetime import datetime
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State


# Test questions
QUESTIONS = """1.Do you own a single-family home or a multi-family home? [MANDATORY]"
"2.Is it a new build or an existing building?"
"3.In what year was it built?"
"""
"""
"4.What is the heated area (m²)?"
"5.Has your house been renovated?"
"6.If yes, what was renovated: windows, roof, walls?"
"7.In what year were your windows replaced?"
"8.Is your roof insulated?"
"9.Are your walls insulated?"
"10.What type of heating system do you currently have, e.g., oil, gas, or electric?"
"11.In what year was your heating system installed?"
"12.Do you have radiators, underfloor heating, or both?"
"13.Does your heating system also heat your hot water?"
"14.What was your average gas consumption in kWh over the last three years? If this information is unavailable, at least over the last 12 months?"
"15.If you heat with oil, how many liters of heating oil did you use in the last 12 months?"
"16.How many people live in your household?"
"17.What is your postal code?"
"18.Do you own the house?"
"19.Are you replacing a functioning gas/oil heating system?"
"""


"""1. What is your house type? (detached, semi-detached, or apartment) [mandatory]
2. What year was your house built?
3. What is the approximate heated floor area in square meters?
"""


def run_conversation_turn(messages: list, user_message: str, questions: str = QUESTIONS) -> tuple:
    """Run a single conversation turn.
    
    Args:
        messages: Current list of messages.
        user_message: User's message for this turn.
        questions: Questions string for the assessment.
        
    Returns:
        Tuple of (updated list of messages, state result dict).
    """
    messages.append(HumanMessage(content=user_message))
    state = State(
    messages=messages,
    questions=questions,
    all_questions_answered=result.get("all_questions_answered", False),
    user_satisfied_with_responses=result.get("user_satisfied_with_responses", False),
    conversation_complete=result.get("conversation_complete", False),
)
    # state = State(**result)
    result = main_graph.invoke(state)
    
    # Add AI response(s) to messages
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg not in messages:
            messages.append(msg)
    
    return messages, result


def print_conversation(messages: list, turn_name: str = ""):
    """Print conversation messages in a clean format.
    
    Args:
        messages: List of messages to print.
        turn_name: Optional name for this turn.
    """
    if turn_name:
        print(f"\n{'='*60}")
        print(f"{turn_name}")
        print(f"{'='*60}\n")
    
    for msg in messages:
        msg_type = "User" if isinstance(msg, HumanMessage) else "AI"
        print(f"{msg_type}: {msg.content}\n")


def save_conversation(messages: list, test_name: str = "conversation"):
    """Save conversation to test_conversations folder.
    
    Args:
        messages: List of messages to save.
        test_name: Name identifier for the test/conversation.
    """
    # Create test_conversations directory if it doesn't exist
    conversations_dir = Path(__file__).parent / "test_conversations"
    conversations_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.json"
    filepath = conversations_dir / filename
    
    # Convert messages to serializable format
    conversation_data = {
        "test_name": test_name,
        "timestamp": timestamp,
        "questions": QUESTIONS,
        "messages": []
    }
    
    for msg in messages:
        msg_data = {
            "type": "user" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content if hasattr(msg, 'content') else str(msg)
        }
        conversation_data["messages"].append(msg_data)
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nConversation saved to: {filepath}")
    return filepath


def test_greeting_only():
    """Test: Initial greeting with no user message."""
    print("\n" + "="*60)
    print("TEST: Greeting Only")
    print("="*60)
    
    messages = []
    state = State(messages=messages, questions=QUESTIONS)
    result = main_graph.invoke(state)
    
    print_conversation(result["messages"])
    save_conversation(result["messages"], "greeting_only")


def test_language_switch():
    """Test: User requests language switch."""
    print("\n" + "="*60)
    print("TEST: Language Switch")
    print("="*60)
    
    messages = []
    messages, _ = run_conversation_turn(messages, "I don't understand. Please speak in English.")
    print_conversation(messages, "After language switch request")
    save_conversation(messages, "language_switch")


def test_sequential_answers():
    """Test: User answers questions one by one."""
    print("\n" + "="*60)
    print("TEST: Sequential Answers")
    print("="*60)
    
    messages = []
    
    # Turn 1: Answer question 1
    messages, _ = run_conversation_turn(messages, "The house type is a detached house.")
    print_conversation(messages, "Turn 1: House type")
    
    # Turn 2: Answer question 2
    messages, _ = run_conversation_turn(messages, "The house was built in 1940.")
    print_conversation(messages, "Turn 2: Year built")
    
    # Turn 3: Answer question 3
    messages, _ = run_conversation_turn(messages, "The heated floor area is 100 square meters.")
    print_conversation(messages, "Turn 3: Floor area")
    save_conversation(messages, "sequential_answers")


def test_all_answers_at_once():
    """Test: User provides all answers in one message."""
    print("\n" + "="*60)
    print("TEST: All Answers at Once")
    print("="*60)
    
    messages = []
    user_message = (
        "My house is a detached house built in 1940. "
        "The heated floor area is 100 square meters."
    )
    messages, _ = run_conversation_turn(messages, user_message)
    print_conversation(messages, "All answers provided")
    save_conversation(messages, "all_answers_at_once")


def test_off_topic_handling():
    """Test: User goes off-topic."""
    print("\n" + "="*60)
    print("TEST: Off-Topic Handling")
    print("="*60)
    
    messages = []
    messages, _ = run_conversation_turn(messages, "What's the weather like today?")
    print_conversation(messages, "Off-topic question")
    save_conversation(messages, "off_topic_handling")


def test_full_conversation():
    """Test: Complete conversation flow from greeting to completion."""
    print("\n" + "="*60)
    print("TEST: Full Conversation Flow with Confirmation")
    print("="*60)
    
    messages = []
    
    # Initial greeting
    state = State(messages=messages, questions=QUESTIONS)
    result = main_graph.invoke(state)
    messages.extend(result["messages"])
    print_conversation(messages, "Initial greeting")
    
    # Answer questions (including edge cases like incomplete answers and language switch)
    answers = [
        "The house type is a detached house.",
        "100",  # Incomplete answer - just a number
        "I don't understand. Please speak in English.",  # Language switch request
        "1940"  # Answer after language switch
    ]
    
    for i, answer in enumerate(answers, 1):
        messages, _ = run_conversation_turn(messages, answer)
        print_conversation(messages, f"After answer {i}: {answer[:50]}...")
    
    # Continue until all questions are answered and confirmation is requested
    # The agent should detect completion and ask for confirmation
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        state = State(messages=messages, questions=QUESTIONS)
        result = main_graph.invoke(state)
        
        # Check if new messages were added
        new_messages = [msg for msg in result["messages"] if msg not in messages]
        if new_messages:
            messages.extend(new_messages)
            print_conversation(messages, f"Iteration {iteration + 1}")
        
        # Check if confirmation was requested (all questions answered)
        if result.get("all_questions_answered", False):
            # Check if confirmation message exists
            has_confirmation = any(
                isinstance(msg, AIMessage) and msg.content and 
                any(phrase in msg.content.lower() for phrase in [
                    "confirm", "is everything correct", "would you like to change",
                    "ist alles korrekt", "möchten sie etwas ändern"
                ])
                for msg in messages
            )
            if has_confirmation:
                print_conversation(messages, "Confirmation requested")
                break
        
        iteration += 1
    
    # User responds to confirmation - wants to change something
    if messages:
        messages, _ = run_conversation_turn(messages, "Actually, I want to change the floor area to 120 square meters.")
        print_conversation(messages, "User requests change")
        
        # Agent handles the change and asks for confirmation again
        state = State(messages=messages, questions=QUESTIONS)
        result = main_graph.invoke(state)
        new_messages = [msg for msg in result["messages"] if msg not in messages]
        if new_messages:
            messages.extend(new_messages)
            print_conversation(messages, "After handling change")
        
        # User confirms everything is correct
        messages, _ = run_conversation_turn(messages, "Yes, everything is correct now.")
        print_conversation(messages, "User confirms")
        
        # Final invocation should generate summary
        state = State(messages=messages, questions=QUESTIONS)
        result = main_graph.invoke(state)
        new_messages = [msg for msg in result["messages"] if msg not in messages]
        if new_messages:
            messages.extend(new_messages)
            print_conversation(messages, "Final summary generated")
    
    # Save conversation
    save_conversation(messages, "full_conversation")


def interactive_mode():
    """Interactive mode: Type answers in the command line."""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("Type your answers. Type 'quit', 'exit', or 'q' to end.")
    print("Press Ctrl+C to exit immediately.\n")
    
    messages = []
    
    # Initial greeting
    state = State(messages=messages, questions=QUESTIONS)
    result = main_graph.invoke(state)
    messages.extend(result["messages"])
    
    # Print initial greeting
    for msg in result["messages"]:
        if isinstance(msg, AIMessage):
            print(f"AI: {msg.content}\n")
    
    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Check for quit commands (case-insensitive, handle variations)
            quit_commands = ['quit', 'exit', 'q', 'stop', 'end']
            if user_input.lower() in quit_commands:
                print("\nSaving conversation...")
                if messages:
                    save_conversation(messages, "interactive")
                print("Goodbye!\n")
                return  # Use return instead of break for cleaner exit
            
            if not user_input:
                continue
            
            # Store message count before to find new messages
            message_count_before = len(messages)
            
            # Run conversation turn (this invokes the graph and adds AI responses)
            messages, result = run_conversation_turn(messages, user_input)
            
            # Print all new AI messages that were added
            new_messages = messages[message_count_before:]
            for msg in new_messages:
                if isinstance(msg, AIMessage):
                    print(f"\nAI: {msg.content}")
            
            # Check if conversation is complete by checking the state flag
            conversation_complete = result.get("conversation_complete", False)
            
            if conversation_complete:
                print("\n" + "="*60)
                print("Conversation complete! Summary has been generated.")
                print("="*60)
                save_conversation(messages, "interactive")
                print("\nYou can continue chatting or type 'quit' to exit.\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving conversation...")
            if messages:
                save_conversation(messages, "interactive")
            print("Goodbye!\n")
            return
        except EOFError:
            print("\n\nEOF detected. Saving conversation...")
            if messages:
                save_conversation(messages, "interactive")
            print("Goodbye!\n")
            return


def main():
    """Run all tests or interactive mode."""
    import sys
    
    # Check if interactive mode is requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive', 'interactive']:
        interactive_mode()
    else:
        # Uncomment the tests you want to run
        # test_greeting_only()
        # test_language_switch()
        # test_sequential_answers()
        # test_all_answers_at_once()
        # test_off_topic_handling()
        test_full_conversation()


if __name__ == "__main__":
    main()
