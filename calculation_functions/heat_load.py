"""
Heat Load Calculation Module

This module contains functions for calculating building heat load using
a cuboid approximation model.
"""

import numpy as np
from typing import Optional


def calculate_heat_load(
    
    t_design: float,
    A: float,
    N_f: int,
    n: float, #Air change rate (1/h)
    U_floor: float,
    U_wall: float,
    U_roof: float,
    U_window: float,
    t_indoor: float = 21,
    h: float = 2.5,
    f_floor: float = 1.0,
    f_wall: float = 1.0,
    f_roof: float = 1.0,
    f_window: float = 1.0,
    is_ground_floor: bool = True,
    is_top_floor: bool = True,
    n_walls_touching: int = 0, #Number of walls touching other buildings/structures (total across all floors)
    f_wall_touching: float = 0.5 #Correction factor for walls touching other buildings
) -> dict:
    """
    Calculate heat load for a building using cuboid approximation.
    
    The building is modeled as stacked cuboid floors, each with:
    - Square floor area (A)
    - Height (h)
    - Windows covering 20% of wall + 2×floor area
    
    Args:
        t_indoor: Indoor design temperature (°C)
        t_design: Outdoor design temperature (°C)
        A: Heated floor area per floor (m²)
        h: Height of each floor (m)
        N_f: Number of floors
        n: Air change rate (1/h)
        U_floor: U-value of floor (W/(m²·K))
        U_wall: U-value of wall (W/(m²·K))
        U_roof: U-value of roof (W/(m²·K))
        U_window: U-value of window (W/(m²·K))
        f_floor: Correction factor for floor (default: 1.0)
        f_wall: Correction factor for wall exposed to air (default: 1.0)
        f_roof: Correction factor for roof (default: 1.0)
        f_window: Correction factor for window (default: 1.0)
        is_ground_floor: Whether building has ground floor (default: True)
        is_top_floor: Whether building has top floor (default: True)
        n_walls_touching: Number of walls touching other buildings/structures 
                          (total across all floors, default: 0)
        f_wall_touching: Correction factor for walls touching other buildings 
                         (default: 0.5)
    
    Returns:
        Dictionary containing:
            - heat_load: Total heat load (W)
            - H_t: Transmission heat transfer coefficient (W/K)
            - H_v: Ventilation heat transfer coefficient (W/K)
            - Dt: Temperature difference (K)
    
    Raises:
        ValueError: If inputs are invalid (negative areas, zero height, etc.)
    """
    # Input validation
    if A <= 0:
        raise ValueError("Floor area A must be positive")
    if h <= 0:
        raise ValueError("Floor height h must be positive")
    if N_f <= 0:
        raise ValueError("Number of floors N_f must be positive")
    if n < 0:
        raise ValueError("Air change rate n cannot be negative")
    if n_walls_touching < 0:
        raise ValueError("Number of walls touching cannot be negative")
    total_walls = 4 * N_f
    if n_walls_touching > total_walls:
        raise ValueError(f"Number of walls touching ({n_walls_touching}) cannot exceed "
                         f"total number of walls ({total_walls})")
    
    # Calculate temperature difference
    Dt = t_indoor - t_design
    
    # Calculate volume per floor
    V = A * h
    
    # Calculate ventilation heat transfer coefficient
    # 0.34 is the volumetric heat capacity of air (Wh/(m³·K))
    H_v = 0.34 * n * V * N_f
    
    # Calculate transmission heat transfer coefficient
    # Floor side length (assuming square floor)
    side_length = np.sqrt(A)
    
    # Floor component (only for ground floor)
    H_t_floor = 0.0
    if is_ground_floor:
        H_t_floor = U_floor * A * f_floor
    
    # Wall component
    # Each wall has area = side_length * h
    wall_area_per_wall = side_length * h
    
    # Total number of walls across all floors: 4 walls per floor × N_f floors
    # This is already calculated as total_walls = 4 * N_f
    
    # Calculate number of exposed walls (not touching other buildings)
    n_walls_exposed = total_walls - n_walls_touching
    
    # Calculate H_t for touching walls and exposed walls separately
    # Total wall area for all floors = wall_area_per_wall * 4 * N_f
    # Split into touching and exposed walls
    H_t_wall_touching = U_wall * wall_area_per_wall * f_wall_touching * n_walls_touching
    H_t_wall_exposed = U_wall * wall_area_per_wall * f_wall * n_walls_exposed
    H_t_wall = H_t_wall_touching + H_t_wall_exposed  # Total H_t for all walls across all floors
    
    # Wall area per floor (for window calculation)
    wall_area_per_floor = 4 * side_length * h
    
    # Roof component (only for top floor)
    H_t_roof = 0.0
    if is_top_floor:
        H_t_roof = U_roof * A * f_roof
    
    # Window component
    # Window area = 20% of (wall area + 2×floor area)
    window_area_per_floor = 0.2 * (wall_area_per_floor + 2 * A)
    H_t_window_per_floor = U_window * window_area_per_floor * f_window
    H_t_window_total = N_f * H_t_window_per_floor
    
    # Calculate total transmission heat transfer coefficient
    # H_t_wall is already calculated as total across all floors
    # H_t_window_total is total across all floors
    # Add floor and roof components
    H_t = H_t_floor + H_t_wall + H_t_window_total + H_t_roof
    
    # Calculate total heat load
    heat_load = (H_t + H_v) * Dt
    
    return {
        'heat_load': heat_load,
        'H_t': H_t,
        'H_v': H_v,
        'Dt': Dt
    }
