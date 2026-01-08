"""
Utility functions for heat load calculations.

This module contains helper functions to extract and calculate
various parameters needed for heat load calculations from JSON data.
"""

from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor


def get_air_change_rate(json_data: Dict[str, Any]) -> float:
    """
    Get air change rate (n) based on building construction year from JSON.
    
    The air change rate can take three values depending on the year:
    - Old buildings (before some year): higher value
    - Medium buildings: medium value
    - New buildings (after some year): lower value
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                   Should contain 'year' key with construction year.
    
    Returns:
        Air change rate n (1/h)
    
    Raises:
        ValueError: If 'year' is missing from JSON data
    
    Note:
        This is a dummy function. Actual implementation should be
        based on building codes and standards for the specific region.
    """
    # Extract year from JSON
    year = json_data.get('year')
    if year is None:
        raise ValueError("Missing required parameter 'year' in JSON data for air change rate calculation")
    
    # Dummy implementation - returns one of three values based on year
    # TODO: Implement actual logic based on building codes
    if year < 1980:
        return 1.5  # Old buildings - higher air change rate
    elif year < 2000:
        return 1.0  # Medium buildings
    else:
        return 0.5  # New buildings - lower air change rate


def get_n_walls_touching(json_data: Dict[str, Any]) -> int:
    """
    Get number of walls touching other buildings/structures.
    
    Args:
        json_data: Dictionary containing building parameters from JSON
    
    Returns:
        Number of walls touching other buildings (total across all floors)
    
    Note:
        This is a dummy function. Actual implementation should extract
        the value from the appropriate JSON key (e.g., 'walls_touching',
        'adjacent_buildings', etc.)
    """
    # Dummy implementation
    # TODO: Extract from JSON key like 'n_walls_touching' or 'walls_touching'
    # For now, return 0 as default
    return json_data.get('n_walls_touching', 0)


def get_u_values(json_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Get U-values for floor, wall, roof, and window from JSON data.
    
    Args:
        json_data: Dictionary containing building parameters from JSON
    
    Returns:
        Dictionary with keys: 'U_floor', 'U_wall', 'U_roof', 'U_window'
        Values are U-values in W/(m²·K)
    
    Note:
        This is a dummy function. Actual implementation should extract
        U-values from the appropriate JSON keys or calculate them based
        on building materials and construction details.
    """
    # Dummy implementation
    # TODO: Extract from JSON keys or calculate from material properties
    # Expected JSON structure might be:
    # {
    #   'u_values': {
    #     'floor': 0.3,
    #     'wall': 0.4,
    #     'roof': 0.25,
    #     'window': 1.2
    #   }
    # }
    
    # Try to get from nested structure first
    if 'u_values' in json_data and isinstance(json_data['u_values'], dict):
        u_vals = json_data['u_values']
        return {
            'U_floor': u_vals.get('floor', 0.3),
            'U_wall': u_vals.get('wall', 0.4),
            'U_roof': u_vals.get('roof', 0.25),
            'U_window': u_vals.get('window', 1.2)
        }
    
    # Fallback to direct keys or defaults
    return {
        'U_floor': json_data.get('U_floor', json_data.get('u_floor', 0.3)),
        'U_wall': json_data.get('U_wall', json_data.get('u_wall', 0.4)),
        'U_roof': json_data.get('U_roof', json_data.get('u_roof', 0.25)),
        'U_window': json_data.get('U_window', json_data.get('u_window', 1.2))
    }


def get_t_design(json_data: Dict[str, Any], database_url: str) -> float:
    """
    Get design temperature (t_design) from database based on location in JSON.
    
    Queries the PostgreSQL database to retrieve the design temperature
    based on location coordinates (latitude/longitude) or location identifier
    from the JSON data.
    
    Args:
        json_data: Dictionary containing building parameters from JSON.
                   Should contain location information such as:
                   - 'latitude' and 'longitude' (for coordinate-based lookup)
                   - OR 'location_id' (for ID-based lookup)
                   - OR 'postal_code' (for postal code-based lookup)
        database_url: PostgreSQL database connection URL
    
    Returns:
        Design temperature t_design (°C)
    
    Raises:
        ValueError: If required location information is missing from JSON
        psycopg2.Error: If database connection or query fails
    
    Note:
        This function queries the database. The exact table name and column
        names should be adjusted based on the actual database schema.
        Expected table might be 'design_temperatures' or 'climate_data'
        with columns like 'latitude', 'longitude', 't_design'.
    """
    # Extract location information from JSON
    # Try multiple possible keys for location
    latitude = json_data.get('latitude') or json_data.get('lat')
    longitude = json_data.get('longitude') or json_data.get('lon') or json_data.get('lng')
    location_id = json_data.get('location_id')
    postal_code = json_data.get('postal_code') or json_data.get('postcode')
    
    if not any([latitude and longitude, location_id, postal_code]):
        raise ValueError(
            "Missing required location information in JSON data. "
            "Need one of: ('latitude' and 'longitude'), 'location_id', or 'postal_code'"
        )
    
    # Connect to database and query
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query based on available location data
        if location_id:
            query = """
                SELECT t_design 
                FROM design_temperatures 
                WHERE location_id = %s
                LIMIT 1
            """
            cursor.execute(query, (location_id,))
        elif postal_code:
            query = """
                SELECT t_design 
                FROM design_temperatures 
                WHERE postal_code = %s
                LIMIT 1
            """
            cursor.execute(query, (postal_code,))
        elif latitude and longitude:
            # Query based on coordinates (might need distance calculation)
            # For now, using exact match - might need to use ST_DWithin for spatial queries
            query = """
                SELECT t_design 
                FROM design_temperatures 
                WHERE ABS(latitude - %s) < 0.01 
                  AND ABS(longitude - %s) < 0.01
                ORDER BY ABS(latitude - %s) + ABS(longitude - %s)
                LIMIT 1
            """
            cursor.execute(query, (latitude, longitude, latitude, longitude))
        else:
            raise ValueError("Unable to determine location from JSON data")
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            raise ValueError(
                f"No design temperature found in database for the provided location. "
                f"Location: lat={latitude}, lon={longitude}, id={location_id}, postal={postal_code}"
            )
        
        return float(result['t_design'])
        
    except psycopg2.Error as e:
        raise psycopg2.Error(f"Database error while fetching design temperature: {e}")
