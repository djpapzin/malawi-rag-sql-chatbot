#!/usr/bin/env python3
import sqlite3
import os
import re
import subprocess

def import_database():
    """Import the database using sqlite3 command line tool"""
    # Define paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, "pmisProjects.db")
    sql_dump_path = os.path.join(root_dir, "pmisProjects.sql")
    processed_sql_path = os.path.join(root_dir, "processed_dump.sql")
    
    # Ensure SQL dump file exists
    if not os.path.exists(sql_dump_path):
        print(f"Error: SQL dump file not found at {sql_dump_path}")
        return
    
    print(f"Processing SQL dump file at {sql_dump_path}")
    
    # Read and preprocess the SQL dump
    try:
        with open(sql_dump_path, 'r', encoding='utf-8', errors='replace') as infile:
            sql_dump = infile.read()
            
        # Remove MySQL specific syntax
        # Remove comments
        sql_dump = re.sub(r'/\*.*?\*/', '', sql_dump, flags=re.DOTALL)
        sql_dump = re.sub(r'--.*?$', '', sql_dump, flags=re.MULTILINE)
        
        # Remove MySQL specific statements
        sql_dump = re.sub(r'SET .*?;', '', sql_dump, flags=re.DOTALL)
        sql_dump = re.sub(r'CREATE DATABASE.*?;', '', sql_dump, flags=re.DOTALL)
        sql_dump = re.sub(r'USE .*?;', '', sql_dump, flags=re.DOTALL)
        sql_dump = re.sub(r'DROP TABLE.*?;', '', sql_dump, flags=re.DOTALL)
        
        # Convert MySQL CREATE TABLE syntax to SQLite
        # Find create table statements
        create_tables = re.findall(r'CREATE TABLE[^;]+;', sql_dump, re.IGNORECASE | re.DOTALL)
        
        for i, create_stmt in enumerate(create_tables):
            # Remove MySQL specific data types and constraints
            modified_stmt = create_stmt
            # Convert data types
            modified_stmt = re.sub(r'`([^`]+)`\s+varchar\(\d+\)', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+char\(\d+\)', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+int\(\d+\)', r'`\1` INTEGER', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+tinyint\(\d+\)', r'`\1` INTEGER', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+smallint\(\d+\)', r'`\1` INTEGER', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+bigint\(\d+\)', r'`\1` INTEGER', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+float(\(\d+,\d+\))?', r'`\1` REAL', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+double(\(\d+,\d+\))?', r'`\1` REAL', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+decimal\(\d+,\d+\)', r'`\1` REAL', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+datetime', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+timestamp', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+date', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+time', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+blob', r'`\1` BLOB', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+text', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'`([^`]+)`\s+longtext', r'`\1` TEXT', modified_stmt, flags=re.IGNORECASE)
            
            # Remove unsupported constraints
            modified_stmt = re.sub(r'AUTO_INCREMENT', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'UNSIGNED', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'CHARACTER SET \w+', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'COLLATE \w+', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'ENGINE\s*=\s*\w+', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'ROW_FORMAT\s*=\s*\w+', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'ON UPDATE CURRENT_TIMESTAMP', '', modified_stmt, flags=re.IGNORECASE)
            modified_stmt = re.sub(r'COMMENT\s*=\s*\'[^\']*\'', '', modified_stmt, flags=re.IGNORECASE)
            
            # Replace the original statement with the modified one
            sql_dump = sql_dump.replace(create_stmt, modified_stmt)
        
        # Fix INSERT statements to be SQLite compatible
        # Find insert statements
        insert_statements = re.findall(r'INSERT INTO[^;]+;', sql_dump, re.IGNORECASE | re.DOTALL)
        
        for i, insert_stmt in enumerate(insert_statements):
            # Replace backticks with double quotes
            modified_insert = insert_stmt.replace('`', '"')
            # Replace the original statement with the modified one
            sql_dump = sql_dump.replace(insert_stmt, modified_insert)
        
        # Write the processed SQL to a file
        with open(processed_sql_path, 'w', encoding='utf-8') as outfile:
            outfile.write(sql_dump)
            
        print(f"Preprocessed SQL dump written to {processed_sql_path}")
    
    except Exception as e:
        print(f"Error preprocessing SQL dump: {e}")
        return
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")
    
    try:
        # Create a new database and import the processed SQL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Created new database at {db_path}")
        
        # Execute SQL file in chunks to avoid memory issues
        with open(processed_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split the script into statements
        statements = sql_script.split(';')
        
        total_statements = len(statements)
        executed_statements = 0
        
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    executed_statements += 1
                    if executed_statements % 100 == 0:
                        print(f"Executed {executed_statements} of {total_statements} statements...")
                except sqlite3.Error as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {stmt[:100]}...")
        
        # Commit changes
        conn.commit()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Database contains {len(tables)} tables:")
        
        # Check record counts for each table
        for table in tables:
            table_name = table[0]
            
            # Skip sqlite_sequence table
            if table_name == 'sqlite_sequence':
                continue
                
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}';")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")
        
        # Close connection
        conn.close()
        
        print(f"Successfully imported database with {executed_statements} statements executed")
        
        # Create symbolic link for backward compatibility
        legacy_path = os.path.join(root_dir, "malawi_projects1.db")
        if os.path.exists(legacy_path):
            os.remove(legacy_path)
            
        try:
            os.symlink(db_path, legacy_path)
            print(f"Created symbolic link from {legacy_path} to {db_path}")
        except OSError:
            # If symlink fails (e.g., on Windows), create a copy
            import shutil
            shutil.copy2(db_path, legacy_path)
            print(f"Created a copy of the database at {legacy_path}")
        
        # Clean up the processed SQL file
        os.remove(processed_sql_path)
        print(f"Removed temporary file {processed_sql_path}")
        
    except Exception as e:
        print(f"Error importing database: {e}")

if __name__ == "__main__":
    import_database() 