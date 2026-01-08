"""
Wrapper function for heat load calculation.

This module provides a high-level interface to calculate heat load
by reading parameters from JSON files and calling the core calculation function.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union

from .heat_load import calculate_heat_load
from .heat_load_utils import (
    get_air_change_rate,
    get_n_walls_touching,
    get_u_values,
    get_t_design
)


def calculate_heat_load_from_json(
    json_path: Union[str, Path],
    database_url: str,
    h: float = 2.5,
    f_floor: float = 1.0,
    f_wall: float = 1.0,
    f_roof: float = 1.0,
    f_window: float = 1.0,
    f_wall_touching: float = 0.5,
    t_indoor: float = 21.0,
    is_ground_floor: bool = True,
    is_top_floor: bool = True
) -> Dict[str, Any]:
    """
    Calculate heat load from JSON input file.
    
    This wrapper function reads building parameters from a JSON file,
    extracts necessary values using utility functions, and calls the
    core heat load calculation function.
    
    Args:
        json_path: Path to JSON file containing building parameters
        database_url: PostgreSQL database connection URL for fetching design temperature
        h: Height of each floor (m), default: 2.5
        f_floor: Correction factor for floor, default: 1.0
        f_wall: Correction factor for wall exposed to air, default: 1.0
        f_roof: Correction factor for roof, default: 1.0
        f_window: Correction factor for window, default: 1.0
        f_wall_touching: Correction factor for walls touching other buildings,
                        default: 0.5
        t_indoor: Indoor design temperature (°C), default: 21.0
        is_ground_floor: Whether building has ground floor, default: True
        is_top_floor: Whether building has top floor, default: True
    
    Returns:
        Dictionary containing:
            - heat_load: Total heat load (W)
            - H_t: Transmission heat transfer coefficient (W/K)
            - H_v: Ventilation heat transfer coefficient (W/K)
            - Dt: Temperature difference (K)
    
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON file is invalid
        ValueError: If required parameters are missing or invalid
    
    Expected JSON structure:
        {
            "area": 100.0,           # Heated floor area per floor (m²)
            "N_f": 2,                # Number of floors
            "year": 1995,            # Construction year (for air change rate)
            "latitude": 52.52,       # Latitude for design temperature lookup
            "longitude": 13.405,     # Longitude for design temperature lookup
            # OR "location_id": "12345",  # Location ID for design temperature lookup
            # OR "postal_code": "10115",   # Postal code for design temperature lookup
            "n_walls_touching": 2,   # Number of walls touching (optional)
            "u_values": {            # U-values (optional, can be direct keys)
                "floor": 0.3,
                "wall": 0.4,
                "roof": 0.25,
                "window": 1.2
            }
        }
    """
    # Read JSON file
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Extract required parameters from JSON
    A = json_data.get('area')
    if A is None:
        raise ValueError("Missing required parameter 'area' in JSON file")
    
    N_f = json_data.get('N_f')
    if N_f is None:
        raise ValueError("Missing required parameter 'N_f' in JSON file")
    
    # Get air change rate from JSON (extracts year internally)
    n = get_air_change_rate(json_data)
    
    # Get U-values from JSON
    u_values = get_u_values(json_data)
    
    # Get number of walls touching
    n_walls_touching = get_n_walls_touching(json_data)
    
    # Get design temperature from database
    t_design = get_t_design(json_data, database_url)
    
    # Call the core calculation function
    result = calculate_heat_load(
        t_design=t_design,
        A=A,
        N_f=N_f,
        n=n,
        U_floor=u_values['U_floor'],
        U_wall=u_values['U_wall'],
        U_roof=u_values['U_roof'],
        U_window=u_values['U_window'],
        t_indoor=t_indoor,
        h=h,
        f_floor=f_floor,
        f_wall=f_wall,
        f_roof=f_roof,
        f_window=f_window,
        is_ground_floor=is_ground_floor,
        is_top_floor=is_top_floor,
        n_walls_touching=n_walls_touching,
        f_wall_touching=f_wall_touching
    )
    
    return result
