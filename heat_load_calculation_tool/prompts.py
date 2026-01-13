"""Prompts for extracting JSON from conversation summaries."""

JSON_EXTRACTION_PROMPT = """You are a helpful assistant that extracts structured data from conversation summaries.

Given a conversation summary about a building/house, extract the following information and return it as valid JSON matching this exact structure:

{{
  "area": <float>,                    // Heated floor area per floor in square meters (m²)
  "N_f": <integer>,                  // Number of floors
  "year": <integer>,                 // Construction year of the building
  "postal_code": <integer>,          // Postal code for the building location
  "n_walls_touching": <integer>,     // Number of walls touching other buildings (default: 0)
  "renovated": <boolean>,            // Whether the house was renovated (default: false)
  "renovations": {{                   // Renovation details object
    "windows": <boolean>,             // Windows renovated (default: false)
    "roof": <boolean>,                // Roof renovated (default: false)
    "walls": <boolean>,               // Walls renovated (default: false)
    "floor": <boolean>                // Floor renovated (default: false)
  }},
  "window_replacement_year": <integer>, // Year windows were replaced (include if mentioned)
  "roof_insulated": <boolean>,       // Whether roof is insulated (default: false)
  "walls_insulated": <boolean>,      // Whether walls are insulated (default: false)
  "h": <float>,                      // Height of each floor in meters (default: 2.5)
  "f_floor": <float>,                // Correction factor for floor (default: 1.0)
  "f_wall": <float>,                 // Correction factor for wall exposed to air (default: 1.0)
  "f_roof": <float>,                 // Correction factor for roof (default: 1.0)
  "f_window": <float>,               // Correction factor for window (default: 1.0)
  "f_wall_touching": <float>,        // Correction factor for walls touching (default: 0.5)
  "t_indoor": <float>,               // Indoor design temperature in Celsius (default: 21.0)
  "is_ground_floor": <boolean>,      // Whether building has ground floor (default: true)
  "is_top_floor": <boolean>          // Whether building has top floor (default: true)
}}

CRITICAL REQUIREMENTS:
1. ALWAYS include ALL fields listed above in the output JSON
2. Use the specified default values for fields not mentioned in the summary
3. Extract actual values from the summary when explicitly mentioned
4. For renovations:
   - If summary mentions renovation, set renovated=true
   - Check which specific elements were renovated (windows, roof, walls, floor)
   - Set corresponding boolean values in the renovations object
5. Include window_replacement_year only if mentioned in the summary
6. Return ONLY valid JSON matching the exact structure above, no additional text, markdown, or explanation
7. Ensure all numeric values use appropriate types (integers for counts/years, floats for measurements/temperatures)

Conversation Summary:
{summary}

Extract and return the JSON data:"""
