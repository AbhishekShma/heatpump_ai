# JSON Input Format for Heat Load Calculation

This document describes the JSON format required for the `calculate_heat_load_from_json` function.

## Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `area` | float | Heated floor area per floor in square meters (m²). Must be positive. | `100.0` |
| `N_f` | int | Number of floors. Must be a positive integer. | `2` |
| `year` | int | Construction year of the building. Used to determine air change rate:<br>- >= 1995: 0.25 (halving ventilation heat losses)<br>- 1977-1994: 0.5 (same losses as room-by-room calculation)<br>- < 1977: 1.0 (doubling ventilation heat losses) | `1995` |
| `postal_code` | int/string | Postal code for design temperature lookup from database. Can also use `postcode` as alternative key. | `81248` |

## Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `n_walls_touching` | int | Number of walls touching other buildings/structures (total across all floors). | `0` |
| `u_values` | object | U-values in W/(m²·K). See U-values section below. | See defaults below |
| `h` | float | Height of each floor in meters (m). | `2.5` |
| `f_floor` | float | Correction factor for floor. | `1.0` |
| `f_wall` | float | Correction factor for wall exposed to air. | `1.0` |
| `f_roof` | float | Correction factor for roof. | `1.0` |
| `f_window` | float | Correction factor for window. | `1.0` |
| `f_wall_touching` | float | Correction factor for walls touching other buildings. | `0.5` |
| `t_indoor` | float | Indoor design temperature in Celsius (°C). | `21.0` |
| `is_ground_floor` | bool | Whether building has ground floor. | `true` |
| `is_top_floor` | bool | Whether building has top floor. | `true` |

### U-values

U-values can be specified in two ways:

#### Option 1: Nested Object (Preferred)
```json
{
  "u_values": {
    "floor": 0.3,
    "wall": 0.4,
    "roof": 0.25,
    "window": 1.2
  }
}
```

#### Option 2: Direct Keys
```json
{
  "U_floor": 0.3,
  "U_wall": 0.4,
  "U_roof": 0.25,
  "U_window": 1.2
}
```

**Default U-values** (if not provided):
- `floor`: 0.3 W/(m²·K)
- `wall`: 0.4 W/(m²·K)
- `roof`: 0.25 W/(m²·K)
- `window`: 1.2 W/(m²·K)

## Complete Example

```json
{
  "area": 100.0,
  "N_f": 2,
  "year": 1995,
  "postal_code": 81248,
  "n_walls_touching": 2,
  "u_values": {
    "floor": 0.3,
    "wall": 0.4,
    "roof": 0.25,
    "window": 1.2
  },
  "h": 2.5,
  "f_floor": 1.0,
  "f_wall": 1.0,
  "f_roof": 1.0,
  "f_window": 1.0,
  "f_wall_touching": 0.5,
  "t_indoor": 21.0,
  "is_ground_floor": true,
  "is_top_floor": true
}
```

## Alternative Keys

- `postal_code` can also be specified as `postcode`
- U-values can use lowercase keys: `u_floor`, `u_wall`, `u_roof`, `u_window`

## Notes

- The `postal_code` must exist in the `climate_info` database table
- All numeric values should be valid numbers (floats or integers)
- The function will raise `ValueError` if required fields are missing
- U-values are optional and will use defaults if not provided
