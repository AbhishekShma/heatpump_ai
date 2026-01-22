EVALUATION_JSON_OUTPUT_SCHEMA = """{{
    "evaluation_results": {{
        "<subsidy_id>": {{
            "subsidy_title": "<title>",
            "is_eligible": True/False,
            "is_model_dependent": True/False,
            "subsidy_percentage": <number or null if not specified>,
            "reasoning": "<brief explanation of why eligible/ineligible>",
            "matched_requirements": ["<list of requirements that were met>"],
            "unmet_requirements": ["<list of requirements not met, if any>"]
        }}
    }},
    "general_subsidies_total": <sum of eligible non-model-dependent subsidy percentages>,
    "model_dependent_subsidies": [
        {{
            "subsidy_id": "<id>",
            "subsidy_title": "<title>",
            "subsidy_percentage": <number>,
            "applicable_heat_pumps": ["<list of heat pump IDs this applies to>"]
        }}
    ]
}}"""
