"""Prompts for extracting JSON from conversation summaries."""

JSON_EXTRACTION_PROMPT = """You are a helpful assistant that extracts structured data from conversation summaries.

Given a conversation summary about a building/house, extract the following information and return it as valid JSON:

Required fields:
- area: Heated floor area per floor in square meters (m²) - float
- N_f: Number of floors - integer
- year: Construction year of the building - integer
- postal_code: Postal code for the building location - integer or string

Optional fields (include if mentioned in summary):
- n_walls_touching: Number of walls touching other buildings - integer (default: 0)
- renovated: Whether the house was renovated - boolean (default: false)
- renovations: Object with keys "windows", "roof", "walls", "floor" - all booleans (default: all false)
- window_replacement_year: Year windows were replaced - integer
- roof_insulated: Whether roof is insulated - boolean (default: false)
- walls_insulated: Whether walls are insulated - boolean (default: false)
- h: Height of each floor in meters - float (default: 2.5)
- f_floor: Correction factor for floor - float (default: 1.0)
- f_wall: Correction factor for wall exposed to air - float (default: 1.0)
- f_roof: Correction factor for roof - float (default: 1.0)
- f_window: Correction factor for window - float (default: 1.0)
- f_wall_touching: Correction factor for walls touching - float (default: 0.5)
- t_indoor: Indoor design temperature in Celsius - float (default: 21.0)
- is_ground_floor: Whether building has ground floor - boolean (default: true)
- is_top_floor: Whether building has top floor - boolean (default: true)

Important extraction rules:
1. Extract only information explicitly mentioned in the summary
2. For missing required fields, use reasonable defaults based on context if possible
3. For renovation questions:
   - If summary mentions renovation, set renovated=true
   - Check which elements were renovated (windows, roof, walls, floor)
   - Set corresponding values in renovations object
4. For insulation:
   - Extract roof_insulated and walls_insulated based on summary
5. Return ONLY valid JSON, no additional text or explanation

Conversation Summary:
{summary}

Return the extracted data as valid JSON:"""
