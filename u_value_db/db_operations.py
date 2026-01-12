"""
Database operations for U-value table.

This module provides functions to insert and manage U-values in the PostgreSQL database.
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from typing import Optional
import os


def get_db_connection(database_url: Optional[str] = None):
    """
    Get database connection.
    
    Args:
        database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL env var.
        
    Returns:
        psycopg2 connection object
        
    Raises:
        ValueError: If database_url is not provided and DATABASE_URL env var is not set
        psycopg2.Error: If connection fails
    """
    if database_url is None:
        database_url = os.getenv('DATABASE_URL')
        if database_url is None:
            raise ValueError(
                "database_url must be provided or DATABASE_URL environment variable must be set"
            )
    
    return psycopg2.connect(database_url)


def create_table_if_not_exists(database_url: Optional[str] = None):
    """
    Create u_values table if it doesn't exist.
    
    Args:
        database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL env var.
        
    Raises:
        psycopg2.Error: If table creation fails
    """
    conn = get_db_connection(database_url)
    cursor = conn.cursor()
    
    try:
        # Create table with primary key
        create_table_query = """
        CREATE TABLE IF NOT EXISTS u_values (
            "Code_Construction" VARCHAR(255) PRIMARY KEY,
            "Code_StatusDataset" VARCHAR(100),
            "Code_Country" VARCHAR(10),
            "Code_ElementType" VARCHAR(50),
            "Code_DataType_Construction" VARCHAR(50),
            "Code_Construction_ConstructionYearClass" VARCHAR(50),
            "Type_Construction" TEXT,
            "Year1_Construction" INTEGER,
            "Year2_Construction" INTEGER,
            "U" NUMERIC,
            "Insulation" VARCHAR(10)
        );
        """
        cursor.execute(create_table_query)
        
        # Create indexes
        index_queries = [
            'CREATE INDEX IF NOT EXISTS idx_element_type ON u_values("Code_ElementType");',
            'CREATE INDEX IF NOT EXISTS idx_data_type ON u_values("Code_DataType_Construction");',
            'CREATE INDEX IF NOT EXISTS idx_country ON u_values("Code_Country");',
            'CREATE INDEX IF NOT EXISTS idx_year_range ON u_values("Year1_Construction", "Year2_Construction");',
            'CREATE INDEX IF NOT EXISTS idx_insulation ON u_values("Insulation");'
        ]
        
        for query in index_queries:
            cursor.execute(query)
        
        conn.commit()
        print("✓ Table and indexes created successfully")
        
    except psycopg2.Error as e:
        conn.rollback()
        raise psycopg2.Error(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_u_values_from_excel(
    excel_path: str,
    database_url: Optional[str] = None,
    clear_existing: bool = False
):
    """
    Insert U-values from Excel file into database.
    
    Args:
        excel_path: Path to Excel file with U-values
        database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL env var.
        clear_existing: If True, delete all existing rows before inserting
        
    Raises:
        FileNotFoundError: If Excel file doesn't exist
        psycopg2.Error: If database operations fail
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    # Load Excel file
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Ensure required columns exist
    required_columns = [
        'Code_Construction', 'Code_StatusDataset', 'Code_Country',
        'Code_ElementType', 'Code_DataType_Construction',
        'Code_Construction_ConstructionYearClass', 'Type_Construction',
        'Year1_Construction', 'Year2_Construction', 'U', 'Insulation'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Create table if it doesn't exist
    create_table_if_not_exists(database_url)
    
    # Connect to database
    conn = get_db_connection(database_url)
    cursor = conn.cursor()
    
    try:
        # Clear existing data if requested
        if clear_existing:
            print("Clearing existing data...")
            cursor.execute('DELETE FROM u_values')
            conn.commit()
            print(f"✓ Deleted existing rows")
        
        # Prepare data for insertion
        # Replace NaN with None for proper NULL handling
        df_clean = df[required_columns].copy()
        df_clean = df_clean.where(pd.notnull(df_clean), None)
        
        # Convert to list of tuples
        records = [tuple(row) for row in df_clean.values]
        
        # Insert with DO NOTHING on conflict
        insert_query = """
        INSERT INTO u_values (
            "Code_Construction", "Code_StatusDataset", "Code_Country",
            "Code_ElementType", "Code_DataType_Construction",
            "Code_Construction_ConstructionYearClass", "Type_Construction",
            "Year1_Construction", "Year2_Construction", "U", "Insulation"
        ) VALUES %s
        ON CONFLICT ("Code_Construction") DO NOTHING
        """
        print(f"Inserting {len(records)} rows...")
        execute_values(cursor, insert_query, records, page_size=1000)
        
        conn.commit()
        
        print(f"✓ Successfully inserted/updated {len(records)} rows")
        
        # Verify insertion
        cursor.execute('SELECT COUNT(*) FROM u_values')
        count = cursor.fetchone()[0]
        print(f"✓ Total rows in database: {count}")
        
    except psycopg2.Error as e:
        conn.rollback()
        raise psycopg2.Error(f"Error inserting data: {e}")
    finally:
        cursor.close()
        conn.close()


def verify_database_contents(
    database_url: Optional[str] = None,
    sample_size: int = 10
):
    """
    Verify database contents by showing sample rows and statistics.
    
    Args:
        database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL env var.
        sample_size: Number of sample rows to display
    """
    conn = get_db_connection(database_url)
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM u_values')
        total_count = cursor.fetchone()[0]
        print(f"Total rows: {total_count}\n")
        
        # Get counts by element type
        cursor.execute("""
            SELECT "Code_ElementType", COUNT(*) as count
            FROM u_values
            GROUP BY "Code_ElementType"
            ORDER BY "Code_ElementType"
        """)
        print("Rows by element type:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Get counts by data type
        cursor.execute("""
            SELECT "Code_DataType_Construction", COUNT(*) as count
            FROM u_values
            GROUP BY "Code_DataType_Construction"
            ORDER BY "Code_DataType_Construction"
        """)
        print("\nRows by data type:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Get sample rows
        cursor.execute(f"""
            SELECT 
                "Code_Construction", "Code_ElementType", 
                "Code_DataType_Construction", "Code_Construction_ConstructionYearClass",
                "Year1_Construction", "Year2_Construction", "U", "Insulation"
            FROM u_values
            LIMIT {sample_size}
        """)
        
        print(f"\nSample rows (first {sample_size}):")
        print("-" * 100)
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | "
                  f"{row[4]}-{row[5]} | U={row[6]} | Insulation={row[7]}")
        
    finally:
        cursor.close()
        conn.close()
