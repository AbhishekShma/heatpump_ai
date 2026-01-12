"""
Script to fill missing year ranges in U-value table.

For missing year classes, uses the highest U value from adjacent year classes
(above and below).
"""
import pandas as pd
import numpy as np


def get_year_class_number(year_class_code):
    """Extract numeric part from year class code (e.g., 'DE.12' -> 12)."""
    return int(year_class_code.split('.')[-1])


def find_adjacent_year_classes(missing_year_class, present_year_classes):
    """
    Find year classes immediately above and below the missing one.
    
    Args:
        missing_year_class: The missing year class code (e.g., 'DE.12')
        present_year_classes: List of present year class codes
        
    Returns:
        Tuple of (year_class_above, year_class_below) or (None, None) if not found
    """
    missing_num = get_year_class_number(missing_year_class)
    present_nums = [get_year_class_number(yc) for yc in present_year_classes]
    
    # Find the year class immediately below (smaller number)
    below_nums = [n for n in present_nums if n < missing_num]
    year_class_below = None
    if below_nums:
        below_num = max(below_nums)
        year_class_below = f"DE.{below_num:02d}"
    
    # Find the year class immediately above (larger number)
    above_nums = [n for n in present_nums if n > missing_num]
    year_class_above = None
    if above_nums:
        above_num = min(above_nums)
        year_class_above = f"DE.{above_num:02d}"
    
    return year_class_above, year_class_below


def get_highest_u_value(df, element_type, data_type, year_classes):
    """
    Get the highest U value from the specified year classes.
    
    Args:
        df: DataFrame with U values
        element_type: Element type (e.g., 'Window')
        data_type: Data type (e.g., 'SyAv')
        year_classes: List of year class codes to check
        
    Returns:
        Highest U value, or None if no values found
    """
    valid_classes = [yc for yc in year_classes if yc is not None]
    if not valid_classes:
        return None
    
    mask = (df['Code_ElementType'] == element_type) & \
           (df['Code_DataType_Construction'] == data_type) & \
           (df['Code_Construction_ConstructionYearClass'].isin(valid_classes))
    
    u_values = df[mask]['U'].values
    if len(u_values) > 0:
        return float(np.max(u_values))
    return None


def generate_code_construction(element_type, data_type, year_class, existing_codes):
    """
    Generate a new Code_Construction following the pattern.
    
    Pattern: DE.{ElementType}.{DataType}.{YearClass}.{Sequence}
    Sequence starts at 01 and increments if code already exists.
    """
    base_code = f"DE.{element_type}.{data_type}.{year_class.replace('DE.', '')}"
    
    # Find the highest sequence number for this base
    sequence = 1
    while True:
        code = f"{base_code}.{sequence:02d}"
        if code not in existing_codes:
            return code
        sequence += 1


def fill_missing_year_ranges(excel_path, year_class_csv_path, output_path):
    """
    Fill missing year ranges in the U-value table.
    
    Args:
        excel_path: Path to input Excel file
        year_class_csv_path: Path to year class CSV file
        output_path: Path to save output Excel file
    """
    # Load data
    df = pd.read_excel(excel_path)
    year_classes_df = pd.read_csv(year_class_csv_path)
    
    # Get expected year classes (excluding DE.00)
    expected_years = sorted(
        [yc for yc in year_classes_df['Code_ConstructionYearClass'].unique() 
         if yc != 'DE.00'],
        key=get_year_class_number
    )
    
    # Create a mapping from year class to year range
    year_class_map = {}
    for _, row in year_classes_df.iterrows():
        yc = row['Code_ConstructionYearClass']
        if yc != 'DE.00':
            year_class_map[yc] = {
                'Year1': int(row['ConstructionYearClass_FirstYear']),
                'Year2': int(row['ConstructionYearClass_LastYear'])
            }
    
    # Collect new rows to add
    new_rows = []
    existing_codes = set(df['Code_Construction'].values)
    
    # Process each element/data type combination
    for (element_type, data_type), group in df.groupby(['Code_ElementType', 'Code_DataType_Construction']):
        present_years = sorted(
            group['Code_Construction_ConstructionYearClass'].unique(),
            key=get_year_class_number
        )
        missing_years = [y for y in expected_years if y not in present_years]
        
        if not missing_years:
            continue
        
        # Get a template row to copy other fields from
        template_row = group.iloc[0].to_dict()
        
        for missing_year in missing_years:
            # Find adjacent year classes
            year_class_above, year_class_below = find_adjacent_year_classes(
                missing_year, present_years
            )
            
            # Get highest U value from adjacent classes
            adjacent_classes = [yc for yc in [year_class_above, year_class_below] if yc is not None]
            highest_u = get_highest_u_value(df, element_type, data_type, adjacent_classes)
            
            if highest_u is None:
                print(f"Warning: Could not find U value for {element_type} - {data_type} - {missing_year}")
                continue
            
            # Get year range
            year_range = year_class_map[missing_year]
            
            # Generate new code
            new_code = generate_code_construction(
                element_type, data_type, missing_year, existing_codes
            )
            existing_codes.add(new_code)
            
            # Create new row
            new_row = template_row.copy()
            new_row['Code_Construction'] = new_code
            new_row['Code_Construction_ConstructionYearClass'] = missing_year
            new_row['Year1_Construction'] = year_range['Year1']
            new_row['Year2_Construction'] = year_range['Year2']
            new_row['U'] = highest_u
            # Type_Construction might need updating, but keeping template for now
            
            new_rows.append(new_row)
            
            print(f"Added {element_type} - {data_type} - {missing_year}: U={highest_u} "
                  f"(from {adjacent_classes})")
    
    # Add new rows to dataframe
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df_updated = pd.concat([df, new_df], ignore_index=True)
        
        # Sort by element type, data type, and year class
        df_updated = df_updated.sort_values(
            by=['Code_ElementType', 'Code_DataType_Construction', 
                'Code_Construction_ConstructionYearClass']
        ).reset_index(drop=True)
        
        # Save to Excel
        df_updated.to_excel(output_path, index=False)
        print(f"\nSuccessfully added {len(new_rows)} new rows.")
        print(f"Output saved to: {output_path}")
    else:
        print("No missing year ranges found to fill.")


if __name__ == '__main__':
    excel_path = '/mnt/d/heatpump_data/u_values/u_value_table_to_modify_with_insulation.xlsx'
    year_class_csv_path = '/mnt/d/heatpump_data/u_values/germany_constr_year_class.csv'
    output_path = '/mnt/d/heatpump_data/u_values/u_value_table_to_modify_with_insulation_filled.xlsx'
    
    fill_missing_year_ranges(excel_path, year_class_csv_path, output_path)
