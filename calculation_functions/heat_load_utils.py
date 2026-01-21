"""
Utility functions for heat load calculations.

This module contains helper functions to extract and calculate
various parameters needed for heat load calculations from JSON data.
"""

from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

def get_air_change_rate(json_data: Dict[str, Any]) -> float:
    """
    Get air change rate (n) based on building construction year from JSON.
    
    The air exchange rates for calculating building heating load differ based on
    the building's construction year:
    - From 1995 onwards: 0.25 (halving ventilation heat losses)
    - 1977 to 1994: 0.5 (same losses as in room-by-room calculation)
    - Before 1977: 1.0 (doubling ventilation heat losses)
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                   Should contain 'year' key with construction year.
    
    Returns:
        Air change rate n (1/h)
    
    Raises:
        ValueError: If 'year' is missing from JSON data
    """
    # Extract year from JSON
    year = json_data.get('year')
    if year is None:
        raise ValueError("Missing required parameter 'year' in JSON data for air change rate calculation")
    
    # Determine air change rate based on construction year
    if year >= 1995:
        return 0.25  # From 1995 onwards - halving ventilation heat losses
    elif year >= 1977:
        return 0.5  # 1977 to 1994 - same losses as room-by-room calculation
    else:
        return 1.0  # Before 1977 - doubling ventilation heat losses


def get_n_walls_touching(json_data: Dict[str, Any]) -> int:
    """
    Get number of walls touching other buildings/structures from JSON.
    
    Extracts the 'n_walls_touching' value from the JSON data. Returns 0 if
    the key is missing or the value is None.
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                   Should contain 'n_walls_touching' key.
    
    Returns:
        Number of walls touching other buildings (total across all floors).
        Returns 0 if the key is missing or value is None.
    """
    return json_data.get('n_walls_touching', 0)


def _normalize_insulation_value(value: Any) -> bool:
    """
    Normalize insulation value from JSON to boolean.
    
    Handles both boolean and string ("yes"/"no") inputs.
    
    Args:
        value: Insulation value from JSON (bool, str, or None)
    
    Returns:
        Boolean True if insulated, False otherwise
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('yes', 'true', '1')
    return False


def _get_u_value_from_db(
    database_url: str,
    element_type: str,
    data_type: str,
    year: Optional[int],
    insulation: Optional[bool] = None,
    country: str = 'DE'
) -> Optional[float]:
    """
    Get U-value from database for a specific element type.
    
    Args:
        database_url: PostgreSQL database connection URL
        element_type: Element type ('Wall', 'Roof', 'Floor', 'Window')
        data_type: Data type ('ReEx' for renovated, 'SyAv' for non-renovated)
        year: Construction year or replacement year. If None, year filter is ignored.
        insulation: Insulation status (True for insulated, False for not insulated), None to ignore filter
        country: Country code, default 'DE'
    
    Returns:
        U-value (W/(m²·K)) or None if not found
    
    Raises:
        psycopg2.Error: If database connection or query fails
    """
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query - use quoted column names to handle case sensitivity
        # For Roof/Wall with insulation='yes', skip Code_DataType_Construction and Code_Country filters
        # (only one row exists for each)
        skip_data_type_country = (insulation is True and 
                                  element_type in ('Roof', 'Wall'))
        
        query = """
        SELECT "U"
        FROM u_value_table_with_insulation
        WHERE "Code_ElementType" = %s
        """
        params = [element_type]
        
        # Add data type and country filters only if not skipping them
        if not skip_data_type_country:
            query += ' AND "Code_DataType_Construction" = %s'
            query += ' AND "Code_Country" = %s'
            params.extend([data_type, country])
        
        # Add year range filter only if year is provided
        if year is not None:
            query += ' AND "Year1_Construction"::integer <= %s AND "Year2_Construction"::integer >= %s'
            params.extend([year, year])
        
        # Add insulation filter if provided - convert boolean to text for database query
        if insulation is not None:
            # Database stores insulation as text ("yes"/"no" or "true"/"false")
            # Convert boolean to text: True -> "yes" or "true", False -> "no" or "false"
            # Based on DB schema, using "yes"/"no" format
            insulation_text = "yes" if insulation else "no"
            query += ' AND "Insulation" = %s'
            params.append(insulation_text)
        
        # Order by U value descending to get highest, limit to 1
        # Cast U to numeric for proper ordering
        query += ' ORDER BY "U"::numeric DESC LIMIT 1'
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is not None:
            # RealDictCursor returns column names without quotes
            # When we SELECT "U", the key in result dict is 'U'
            u_value = result.get('U')
            
            # If not found, try lowercase (shouldn't happen but safe)
            if u_value is None:
                u_value = result.get('u')
            
            # If still not found, get first value (fallback)
            if u_value is None and result:
                u_value = list(result.values())[0]
            
            if u_value is not None:
                # Convert to float (U is stored as text, so convert string to float)
                return float(str(u_value))
        return None
        
    except psycopg2.Error as e:
        raise psycopg2.Error(f"Database error while fetching U-value: {e}")
    except Exception as e:
        # Catch any other errors (like KeyError for column access)
        raise psycopg2.Error(f"Error accessing database result: {e}")


def get_u_values(json_data: Dict[str, Any], database_url: Optional[str] = None) -> Dict[str, float]:
    """
    Get U-values for floor, wall, roof, and window from JSON data or database.
    
    If database_url is provided and renovation information is available,
    U-values are extracted from the database based on renovation status,
    insulation, and year. Otherwise, requires u_values to be provided in JSON.
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                  Expected keys:
                  - 'year': Construction year (required for DB lookup)
                  - 'renovated': Boolean indicating if house was renovated
                  - 'renovations': Dict with keys 'windows', 'roof', 'walls', 'floor' (booleans)
                  - 'window_replacement_year': Year windows were replaced (optional)
                  - 'roof_insulated': Boolean indicating if roof is insulated
                  - 'walls_insulated': Boolean indicating if walls are insulated
                  - 'u_values': Dict with manual U-values (required if database_url is None or lookup fails)
        database_url: PostgreSQL database connection URL (optional)
    
    Returns:
        Dictionary with keys: 'U_floor', 'U_wall', 'U_roof', 'U_window'
        Values are U-values in W/(m²·K)
    
    Raises:
        ValueError: If required U-values are missing and cannot be retrieved from database
    """
    # Helper function to extract U-values from JSON
    def _extract_u_values_from_json(json_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract U-values from JSON, raising error if missing."""
        if 'u_values' in json_data and isinstance(json_data['u_values'], dict):
            u_vals = json_data['u_values']
            missing = []
            if 'floor' not in u_vals:
                missing.append('floor')
            if 'wall' not in u_vals:
                missing.append('wall')
            if 'roof' not in u_vals:
                missing.append('roof')
            if 'window' not in u_vals:
                missing.append('window')
            
            if missing:
                raise ValueError(f"Missing required U-values in 'u_values': {', '.join(missing)}")
            
            return {
                'U_floor': u_vals['floor'],
                'U_wall': u_vals['wall'],
                'U_roof': u_vals['roof'],
                'U_window': u_vals['window']
            }
        
        # Try direct keys
        missing = []
        u_floor = json_data.get('U_floor') or json_data.get('u_floor')
        u_wall = json_data.get('U_wall') or json_data.get('u_wall')
        u_roof = json_data.get('U_roof') or json_data.get('u_roof')
        u_window = json_data.get('U_window') or json_data.get('u_window')
        
        if u_floor is None:
            missing.append('U_floor')
        if u_wall is None:
            missing.append('U_wall')
        if u_roof is None:
            missing.append('U_roof')
        if u_window is None:
            missing.append('U_window')
        
        if missing:
            raise ValueError(f"Missing required U-values: {', '.join(missing)}")
        
        return {
            'U_floor': u_floor,
            'U_wall': u_wall,
            'U_roof': u_roof,
            'U_window': u_window
        }
    
    # If database_url not provided, require JSON values
    if database_url is None:
        return _extract_u_values_from_json(json_data)
    
    # Extract year and renovation info
    year = json_data.get('year')
    if year is None:
        # If year missing, require JSON values
        return _extract_u_values_from_json(json_data)
    
    renovated = json_data.get('renovated', False)
    renovations = json_data.get('renovations', {})
    
    u_values = {}
    
    # Get window U-value
    window_renovated = renovations.get('windows', False) if renovated else False
    window_year = json_data.get('window_replacement_year', year)
    window_data_type = 'ReEx' if window_renovated else 'SyAv'
    window_u = _get_u_value_from_db(database_url, 'Window', window_data_type, window_year)
    if window_u is None:
        # Fallback to SyAv with highest U-value
        window_u = _get_u_value_from_db(database_url, 'Window', 'SyAv', window_year)
    if window_u is None:
        # If still None, try to get from JSON
        u_vals = json_data.get('u_values', {})
        if isinstance(u_vals, dict) and 'window' in u_vals:
            window_u = u_vals['window']
        else:
            window_u = json_data.get('U_window') or json_data.get('u_window')
        if window_u is None:
            raise ValueError(f"Could not retrieve U-value for window from database or JSON")
    u_values['U_window'] = window_u
    
    # Get roof U-value
    roof_renovated = renovations.get('roof', False) if renovated else False
    roof_insulated = _normalize_insulation_value(json_data.get('roof_insulated', False))
    roof_data_type = 'ReEx' if roof_renovated else 'SyAv'
    
    # PRIORITY: If insulated, get ONLY insulation='yes' values
    # For roof with insulation='yes', only one row exists (skips data_type and country filters)
    if roof_insulated:
        roof_u = _get_u_value_from_db(database_url, 'Roof', 'ReEx', None, True)
        # No fallback without insulation filter - must have Insulation='yes'
    elif roof_renovated and not roof_insulated:
        # Case 2: Renovated + Insulated = no → Use highest U-value with Insulation='no'
        roof_u = _get_u_value_from_db(database_url, 'Roof', 'ReEx', year, False)
    else:
        # Case 3: Not renovated and not insulated → Use highest U-value (SyAv, no insulation filter)
        roof_u = _get_u_value_from_db(database_url, 'Roof', 'SyAv', year)
    
    if roof_u is None and not roof_insulated:
        # Fallback to SyAv with highest U-value (no insulation filter) - only if NOT insulated
        roof_u = _get_u_value_from_db(database_url, 'Roof', 'SyAv', year)
    if roof_u is None:
        # If still None, try to get from JSON
        u_vals = json_data.get('u_values', {})
        if isinstance(u_vals, dict) and 'roof' in u_vals:
            roof_u = u_vals['roof']
        else:
            roof_u = json_data.get('U_roof') or json_data.get('u_roof')
        if roof_u is None:
            raise ValueError(f"Could not retrieve U-value for roof from database or JSON")
    u_values['U_roof'] = roof_u
    
    # Get wall U-value
    wall_renovated = renovations.get('walls', False) if renovated else False
    wall_insulated = _normalize_insulation_value(json_data.get('walls_insulated', False))
    wall_data_type = 'ReEx' if wall_renovated else 'SyAv'
    
    # PRIORITY: If insulated, get ONLY insulation='yes' values
    # For wall with insulation='yes', only one row exists (skips data_type and country filters)
    if wall_insulated:
        wall_u = _get_u_value_from_db(database_url, 'Wall', 'ReEx', None, True)
        # No fallback without insulation filter - must have Insulation='yes'
    elif wall_renovated and not wall_insulated:
        # Case 2: Renovated + Insulated = no → Use highest U-value with Insulation='no'
        wall_u = _get_u_value_from_db(database_url, 'Wall', 'ReEx', year, False)
    else:
        # Case 3: Not renovated and not insulated → Use highest U-value (SyAv, no insulation filter)
        wall_u = _get_u_value_from_db(database_url, 'Wall', 'SyAv', year)
    
    if wall_u is None and not wall_insulated:
        # Fallback to SyAv with highest U-value (no insulation filter) - only if NOT insulated
        wall_u = _get_u_value_from_db(database_url, 'Wall', 'SyAv', year)
    if wall_u is None:
        # If still None, try to get from JSON
        u_vals = json_data.get('u_values', {})
        if isinstance(u_vals, dict) and 'wall' in u_vals:
            wall_u = u_vals['wall']
        else:
            wall_u = json_data.get('U_wall') or json_data.get('u_wall')
        if wall_u is None:
            raise ValueError(f"Could not retrieve U-value for wall from database or JSON")
    u_values['U_wall'] = wall_u
    
    # Get floor U-value
    floor_renovated = renovations.get('floor', False) if renovated else False
    floor_data_type = 'ReEx' if floor_renovated else 'SyAv'
    # No insulation filter for floors
    floor_u = _get_u_value_from_db(database_url, 'Floor', floor_data_type, year)
    if floor_u is None:
        # Fallback to SyAv with highest U-value
        floor_u = _get_u_value_from_db(database_url, 'Floor', 'SyAv', year)
    if floor_u is None:
        # If still None, try to get from JSON
        u_vals = json_data.get('u_values', {})
        if isinstance(u_vals, dict) and 'floor' in u_vals:
            floor_u = u_vals['floor']
        else:
            floor_u = json_data.get('U_floor') or json_data.get('u_floor')
        if floor_u is None:
            raise ValueError(f"Could not retrieve U-value for floor from database or JSON")
    u_values['U_floor'] = floor_u
    
    return u_values


def get_t_design(json_data: Dict[str, Any], database_url: str) -> float:
    """
    Get design temperature (t_design) from database based on postal code.
    
    Queries the PostgreSQL database 'climate_info' table to retrieve the design
    temperature based on postal code from the JSON data.
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                   Must contain 'postal_code' or 'postcode' key.
        database_url: PostgreSQL database connection URL
    
    Returns:
        Design temperature t_design (°C)
    
    Raises:
        ValueError: If postal_code is missing from JSON data or not found in database
        psycopg2.Error: If database connection or query fails
    """
    # Extract postal code from JSON
    postal_code = json_data.get('postal_code') or json_data.get('postcode')
    
    if not postal_code:
        raise ValueError(
            "Missing required parameter 'postal_code' in JSON data for design temperature lookup"
        )
    
    # Connect to database and query
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query climate_info table using postal_code
        query = """
        SELECT design_temperature 
        FROM climate_info 
            WHERE postal_code = %s
            LIMIT 1
        """
        cursor.execute(query, (postal_code,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            raise ValueError(
                f"No design temperature found in database for postal code: {postal_code}"
            )
        
        return float(result['design_temperature'])
        
    except psycopg2.Error as e:
        raise psycopg2.Error(f"Database error while fetching design temperature: {e}")

def normalize(value):
    if isinstance(value, np.generic):
        return value.item()
    return value