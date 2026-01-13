"""Example usage of the summary generation agent."""

import json
from langchain_core.messages import HumanMessage, AIMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State


def main():
    """Example of how to use the summary generation agent."""
    
    # Conversation data: User responses and calculated values
    conversation_data = {
        "heat_load": 8.5,
        "transmission_heat_loss": 6.2,
        "ventilation_heat_loss": 2.3
    }
    
    # Building data: Building parameters matching input_example.json format
    building_data = {
        "area": 100.0,
        "N_f": 2,
        "year": 1995,
        "postal_code": 81248,
        "n_walls_touching": 2,
        "renovated": True,
        "renovations": {
            "windows": True,
            "roof": True,
            "walls": False,
            "floor": False
        },
        "window_replacement_year": 2015,
        "roof_insulated": True,
        "walls_insulated": False,
        "h": 2.5,
        "f_floor": 1.0,
        "f_wall": 1.0,
        "f_roof": 1.0,
        "f_window": 1.0,
        "f_wall_touching": 0.5,
        "t_indoor": 21.0,
        "is_ground_floor": True,
        "is_top_floor": True
    }
    
    # Sample conversation history
    messages = [
        HumanMessage(content="My house is a two-story building built in 1995."),
        AIMessage(content="Thank you for that information. Can you tell me about the floor area?"),
        HumanMessage(content="The heated floor area is about 100 square meters per floor."),
        AIMessage(content="Great! Have you done any renovations?"),
        HumanMessage(content="Yes, we replaced the windows in 2015 and renovated the roof. The roof is also insulated now."),
        AIMessage(content="That's helpful information. How many walls are touching other buildings?"),
        HumanMessage(content="Two walls are touching adjacent buildings.")
    ]
    
    print("=== Summary Generation Example ===\n")
    print("Conversation Data (User Responses & Calculations):")
    print(json.dumps(conversation_data, indent=2))
    print("\n" + "="*50 + "\n")
    
    print("Building Data (Building Parameters):")
    print(json.dumps(building_data, indent=2))
    print("\n" + "="*50 + "\n")
    
    print("Conversation History:")
    for i, msg in enumerate(messages, 1):
        msg_type = "User" if isinstance(msg, HumanMessage) else "AI"
        print(f"{i}. {msg_type}: {msg.content}")
    print("\n" + "="*50 + "\n")
    
    # Create state with messages and both JSON structures
    state = State(
        messages=messages, 
        conversation_data=conversation_data,
        building_data=building_data
    )
    
    # Invoke the graph
    print("Generating summary...\n")
    result = main_graph.invoke(state)
    
    # Display the generated summary
    print("Generated Summary:")
    print("-" * 50)
    print(result['summary'])
    print("-" * 50)


if __name__ == "__main__":
    main()
