import sqlite3
import pandas as pd
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sqlite_schema():
    """Create SQLite schema from MySQL dump"""
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pmisProjects.sql')
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Extract CREATE TABLE statement
    create_table = re.search(r'create table.*?\(.*?\);', sql, re.DOTALL | re.IGNORECASE).group()
    
    # Convert MySQL types to SQLite
    create_table = create_table.replace('`', '"')
    create_table = re.sub(r'varchar\s*\(\d+\)', 'TEXT', create_table)
    create_table = re.sub(r'decimal\s*\(\d+\)', 'REAL', create_table)
    create_table = re.sub(r'float', 'REAL', create_table)
    create_table = re.sub(r'tinyint\s*\(\d+\)', 'INTEGER', create_table)
    create_table = re.sub(r'int\s*\(\d+\)', 'INTEGER', create_table)
    create_table = create_table.replace('date', 'TEXT')  # SQLite doesn't have a native DATE type
    
    return create_table

def extract_insert_data(sql_file):
    """Extract data from INSERT statements"""
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Extract column names from CREATE TABLE
    create_match = re.search(r'create table.*?\((.*?)\);', sql, re.DOTALL | re.IGNORECASE)
    columns = re.findall(r'`(\w+)`', create_match.group(1))
    
    # Extract column names from INSERT statements
    insert_columns = None
    for line in sql.split('\n'):
        if line.lower().startswith('insert into'):
            match = re.search(r'insert into.*?\((.*?)\)', line, re.IGNORECASE)
            if match:
                insert_columns = re.findall(r'`(\w+)`', match.group(1))
                break
    
    if not insert_columns:
        insert_columns = columns
    
    # Create a mapping of insert columns to table columns
    col_mapping = {i: columns.index(col) if col in columns else -1 
                  for i, col in enumerate(insert_columns)}
    
    # Extract values from INSERT statements
    insert_pattern = r"values\s*\((.*?)\)"
    rows = []
    for match in re.finditer(insert_pattern, sql, re.DOTALL):
        values = match.group(1).split(',')
        # Clean up values
        cleaned_values = [None] * len(columns)  # Initialize with NULL for all columns
        for i, val in enumerate(values):
            if i in col_mapping and col_mapping[i] != -1:
                val = val.strip()
                if val.upper() == 'NULL':
                    cleaned_values[col_mapping[i]] = None
                else:
                    # Remove quotes and handle special cases
                    val = val.strip("'")
                    if val == '':
                        cleaned_values[col_mapping[i]] = None
                    else:
                        cleaned_values[col_mapping[i]] = val
        rows.append(cleaned_values)
    
    return columns, rows

def create_markdown_schema(columns):
    """Generate Markdown documentation of the schema"""
    markdown = """# Project Management Information System Database Schema

## Table: proj_dashboard

| Column Name | Description | Type |
|------------|-------------|------|
"""
    
    type_mapping = {
        'TEXT': 'Text',
        'REAL': 'Decimal',
        'INTEGER': 'Integer',
        'DATE': 'Date'
    }
    
    for col in columns:
        # Infer description from column name
        words = re.findall('[A-Z][^A-Z]*', col) if col.isupper() else col.split('_')
        description = ' '.join(words).title()
        
        # Infer type from column name
        if 'DATE' in col.upper():
            col_type = 'DATE'
        elif 'UUID' in col.upper() or 'NAME' in col.upper() or 'DESC' in col.upper():
            col_type = 'TEXT'
        elif 'BINARY' in col.upper():
            col_type = 'INTEGER'
        elif any(word in col.upper() for word in ['TOTAL', 'BUDGET', 'VALUE', 'AMOUNT']):
            col_type = 'REAL'
        else:
            col_type = 'TEXT'
            
        markdown += f"| {col} | {description} | {type_mapping[col_type]} |\n"
    
    return markdown

def main():
    try:
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(__file__))
        sql_file = os.path.join(base_dir, 'pmisProjects.sql')
        
        logger.info(f"Processing SQL file: {sql_file}")
        
        # Create SQLite database
        sqlite_db = os.path.join(base_dir, "pmisProjects.db")
        if os.path.exists(sqlite_db):
            os.remove(sqlite_db)
        
        conn = sqlite3.connect(sqlite_db)
        cursor = conn.cursor()
        
        # Create table
        create_table = create_sqlite_schema()
        logger.info("Creating table schema...")
        cursor.execute(create_table)
        
        # Insert data
        logger.info("Extracting data from SQL file...")
        columns, rows = extract_insert_data(sql_file)
        
        logger.info(f"Found {len(columns)} columns and {len(rows)} rows")
        logger.info(f"First row has {len(rows[0])} values")
        
        placeholders = ','.join(['?' for _ in columns])
        insert_sql = f'INSERT INTO "proj_dashboard" VALUES ({placeholders})'
        
        logger.info("Inserting data into SQLite database...")
        cursor.executemany(insert_sql, rows)
        conn.commit()
        
        # Export to CSV
        logger.info("Exporting to CSV...")
        df = pd.read_sql_query("SELECT * FROM proj_dashboard", conn)
        csv_file = os.path.join(base_dir, "pmisProjects.csv")
        df.to_csv(csv_file, index=False)
        
        # Generate Markdown documentation
        logger.info("Generating schema documentation...")
        markdown = create_markdown_schema(columns)
        md_file = os.path.join(base_dir, "DATABASE_SCHEMA.md")
        with open(md_file, "w") as f:
            f.write(markdown)
        
        conn.close()
        
        logger.info("Conversion complete!")
        logger.info(f"- Created SQLite database: {sqlite_db}")
        logger.info(f"- Created CSV export: {csv_file}")
        logger.info(f"- Created schema documentation: {md_file}")
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise

if __name__ == "__main__":
    main()
