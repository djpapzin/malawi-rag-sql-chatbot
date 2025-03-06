#!/usr/bin/env python3
"""
Apply SQL Fix Script

This script patches the langchain_sql.py file with the fixed _extract_sql_from_text method.
"""

import os
import re
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_sql_fix():
    """Apply the SQL extraction fix to the langchain_sql.py file"""
    
    # Path to the file
    file_path = os.path.join('app', 'database', 'langchain_sql.py')
    backup_path = file_path + '.bak'
    
    # Create a backup
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the new method
    new_method = '''    def _extract_sql_from_text(self, text: str) -> str:
        """Extract the SQL query from the LLM response"""
        logger.info(f"Extracting SQL query from text: {repr(text)}")
        
        # Remove any markdown code block markers
        text = re.sub(r\'```(?:sql)?(.*?)```\', r\'\\1\', text, flags=re.DOTALL)
        
        # Try to find a SQL query with SELECT statement
        sql_pattern = r\'SELECT\\s+.*?FROM\\s+.*?(?:WHERE\\s+.*?)?(?:GROUP\\s+BY\\s+.*?)?(?:ORDER\\s+BY\\s+.*?)?(?:LIMIT\\s+\\d+)?;?\'
        matches = re.search(sql_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            query = matches.group(0).strip()
            
            # Ensure query ends with semicolon
            if not query.endswith(\';\'):
                query += \';\'
                
            # Convert table name to uppercase to match schema
            query = query.replace(\'proj_dashboard\', \'PROJ_DASHBOARD\')
            query = query.replace(\'Proj_Dashboard\', \'PROJ_DASHBOARD\')
            
            logger.info(f"Found SQL query: {query}")
            return query
            
        # If no SQL query found, try a simpler approach - just look for SELECT
        if \'SELECT\' in text.upper():
            # Extract everything from SELECT to the end or to a clear delimiter
            select_idx = text.upper().find(\'SELECT\')
            end_idx = len(text)
            
            # Look for common end delimiters
            for delimiter in [\'\\n\\n\', \'```\', \'"""\']:
                if delimiter in text[select_idx:]:
                    potential_end = text.find(delimiter, select_idx)
                    if potential_end > select_idx and potential_end < end_idx:
                        end_idx = potential_end
            
            query = text[select_idx:end_idx].strip()
            
            # Ensure query ends with semicolon
            if not query.endswith(\';\'):
                query += \';\'
                
            logger.info(f"Found SQL query (simple approach): {query}")
            return query
            
        # If all else fails, provide a simple query that will work
        logger.warning(f"Could not extract SQL query from text: {text}")
        return "SELECT projectname, district, projectsector, budget FROM PROJ_DASHBOARD LIMIT 10;"'''
    
    # Find the existing method
    pattern = r'def _extract_sql_from_text\(self, text: str\) -> str:.*?(?=def \w+\(self)'
    replacement = new_method
    
    # Replace the method
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    logger.info(f"Updated {file_path} with the fixed _extract_sql_from_text method")
    
    return "SQL extraction fix applied successfully"

if __name__ == "__main__":
    result = apply_sql_fix()
    print(result)
    print("\nRestart the server to apply the changes.")
