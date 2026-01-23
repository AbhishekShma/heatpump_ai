from langchain_core.messages import HumanMessage, AIMessage
from graphs.main_graph import main_graph
from graphs.schemas.state_schema import State

QUESTIONS = """1.Do you own a single-family home or a multi-family home? [MANDATORY]"
"2.Is it a new build or an existing building?"
"3.In what year was it built? [MANDATORY]"
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

def interactive_mode():
    messages = []
    last_result = {}
    x = main_graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(x)
    # initial invoke
    state = State(messages=messages, questions=QUESTIONS)
    last_result = main_graph.invoke(state)
    messages = last_result["messages"]

    # print only initial AI output
    for msg in messages:
        if isinstance(msg, AIMessage):
            print(msg.content)

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            return

        if not user_input:
            continue

        before = len(messages)
        messages.append(HumanMessage(content=user_input))

        state = State(
            messages=messages,
            questions=QUESTIONS,
            all_questions_answered=last_result.get("all_questions_answered", False),
            user_satisfied_with_responses=last_result.get("user_satisfied_with_responses", False),
            conversation_complete=last_result.get("conversation_complete", False),
        )

        last_result = main_graph.invoke(state)
        messages = last_result["messages"]

        for msg in messages[before:]:
            if isinstance(msg, AIMessage):
                print(msg.content)

        if last_result.get("conversation_complete", False):
            return


if __name__ == "__main__":
    interactive_mode()