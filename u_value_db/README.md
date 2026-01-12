# U-Value Database Operations

This module provides functionality to insert and manage U-values in the PostgreSQL database.

## Structure

- `db_operations.py`: Core database operations (create table, insert data, verify)
- `insert_u_values_to_db.ipynb`: Jupyter notebook to insert U-values from Excel to database

## Prerequisites

1. PostgreSQL database with connection URL
2. Python packages: `pandas`, `openpyxl`, `psycopg2-binary`
3. Excel file with U-values (filled with all year ranges)

## Usage

### Using the Jupyter Notebook

1. Open `insert_u_values_to_db.ipynb`
2. Set the `DATABASE_URL` environment variable or modify it in the notebook
3. Update `EXCEL_FILE_PATH` to point to your filled U-value Excel file
4. Run all cells sequentially

### Using Python Script

```python
from u_value_db.db_operations import (
    insert_u_values_from_excel,
    verify_database_contents
)

# Insert U-values from Excel
insert_u_values_from_excel(
    excel_path='/path/to/u_value_table.xlsx',
    database_url='postgresql://user:password@host:port/database',
    clear_existing=False  # Set to True to clear existing data first
)

# Verify insertion
verify_database_contents(database_url='postgresql://...')
```

## Database Schema

The table `u_values` has the following columns:

- `Code_Construction` (VARCHAR, PRIMARY KEY)
- `Code_StatusDataset` (VARCHAR)
- `Code_Country` (VARCHAR)
- `Code_ElementType` (VARCHAR) - e.g., 'Window', 'Wall', 'Roof', 'Floor'
- `Code_DataType_Construction` (VARCHAR) - 'ReEx' or 'SyAv'
- `Code_Construction_ConstructionYearClass` (VARCHAR) - e.g., 'DE.01', 'DE.12'
- `Type_Construction` (TEXT)
- `Year1_Construction` (INTEGER)
- `Year2_Construction` (INTEGER)
- `U` (NUMERIC) - U-value in W/(m²·K)
- `Insulation` (VARCHAR) - 'yes' or 'no'

## Features

- **Automatic table creation**: Creates the table if it doesn't exist
- **Upsert operation**: Updates existing rows or inserts new ones based on `Code_Construction`
- **Batch insertion**: Efficiently inserts data using `execute_values`
- **Verification**: Provides functions to verify database contents and statistics
- **Index creation**: Automatically creates indexes for common query patterns

## Notes

- The insertion uses `ON CONFLICT` to handle duplicates (updates existing rows)
- Set `clear_existing=True` with caution - it will delete all existing data
- The module matches the database schema expected by `heat_load_utils.py`
