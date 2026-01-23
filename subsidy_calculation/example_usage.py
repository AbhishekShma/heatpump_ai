"""
Example usage of the subsidy calculation module.
Questions are kept EXACTLY as stored in the questions table.
"""

import json
from calculate_subsidies import calculate_subsidies


# ---------------------------------------------------------------------
# Example user responses – QUESTIONS KEPT AS-IS (verbatim)
# ---------------------------------------------------------------------
example_questions_chat = """
    "Do you own a single-family home or a multi-family home?": "single-family home",
    "Is it a new build or an existing building?": "existing building",
    "In what year was it built?": 1986,
    "What is the heated area (m²)?": 120,
    "Has your house been renovated?": "yes",
    "If yes, what was renovated: windows, roof, walls?": "windows, roof",
    "In what year were your windows replaced?": 2018,
    "Is your roof insulated?": "yes",
    "Are your walls insulated?": "no",
    "What type of heating system do you currently have, e.g., oil, gas, or electric?": "oil",
    "In what year was your heating system installed?": 2002,
    "Do you have radiators, underfloor heating, or both?": "radiators",
    "Does your heating system also heat your hot water?": "yes",
    "What was your average gas consumption in kWh over the last three years? If this information is unavailable, at least over the last 12 months?": None,
    "If you heat with oil, how many liters of heating oil did you use in the last 12 months?": 2200,
    "How many people live in your household?": 3,
    "What is your postal code?": "80331",
    "Do you own the house?": "yes",
    "Are you replacing a functioning gas/oil heating system?": "yes"
"""


# ---------------------------------------------------------------------
# Subsidy table (unchanged)
# ---------------------------------------------------------------------
example_subsidy_table = {
    "1": {
        "sub_id": 1,
        "title": "Basic Heat Pump Subsidy",
        "description": "30% basic subsidy for all heat pumps that we recommend. But this and all other subsidies are only to be applied if the house is older than 20 years, if not, no subsidy is applied, at all.",
        "is_active": True
    },
    "2": {
        "sub_id": 2,
        "title": "Climate Speed Bonus",
        "description": (
            "20% climate speed bonus for owner-occupied residential units. "
            "Applies when replacing a functional heating system that is older than 20 years."
        ),
        "is_active": True
    },
    "3": {
        "sub_id": 3,
        "title": "Income-Based Bonus",
        "description": (
            "30% income bonus for owner-occupier homeowners with a taxable annual "
            "household income of up to 40,000 euros."
        ),
        "is_active": True
    },
    "4": {
        "sub_id": 4,
        "title": "Efficiency Bonus",
        "description": (
            "5% efficiency bonus for heat pumps if air,water, soil, or wastewater is used "
            "as a heat source or if a natural refrigerant is used."
        ),
        "is_active": True
    }
}



# ---------------------------------------------------------------------
# Heat pump list – DIRECTLY based on your ACTUAL heat pump table
# ---------------------------------------------------------------------
example_heat_pump_list = [
    {
        "id": "hp_001",
        "Manufacturer": "Bosch Thermotechnik GmbH",
        "Type": "CL7000i 20 E",
        "heat_output_35_C_in_kw": 2.3,
        "effeciency_35_C": 201,
        "Refrigerant": "R32",
        "category": "Luft / Luft (Heizleistung <= 12 kW)"
    },
    {
        "id": "hp_002",
        "Manufacturer": "Bosch Thermotechnik GmbH",
        "Type": "CL7000i 26 E",
        "heat_output_35_C_in_kw": 4.1,
        "effeciency_35_C": 201,
        "Refrigerant": "R32",
        "category": "Luft / Luft (Heizleistung <= 12 kW)"
    },
    {
        "id": "hp_003",
        "Manufacturer": "Bosch Thermotechnik GmbH",
        "Type": "CL7000i 53 E",
        "heat_output_35_C_in_kw": 5.6,
        "effeciency_35_C": 181,
        "Refrigerant": "R32",
        "category": "Luft / Luft (Heizleistung <= 12 kW)"
    }
]

stopping_criteria = "If the house is newer than 20 years, then no subsidy is applied, at all."

def main():
    print("=" * 60)
    print("SUBSIDY CALCULATION")
    print("=" * 60)

    print("\nUser responses (raw):")
    print(example_questions_chat)

    print("\nHeat pumps:")
    for hp in example_heat_pump_list:
        print(
            f"- {hp['Manufacturer']} {hp['Type']} | "
            f"{hp['heat_output_35_C_in_kw']} kW @35°C | "
            f"{hp['Refrigerant']}"
        )

    print("\nRunning subsidy calculation...")
    print("-" * 60)

    result = calculate_subsidies(
        questions_chat=example_questions_chat,
        subsidy_table=example_subsidy_table,
        recommended_heat_pump_list=example_heat_pump_list,
        stopping_criteria=stopping_criteria
    )

    print("\nRESULT:")
    print(result["subsidy_calculation_evaluation_results"])


if __name__ == "__main__":
    main()
