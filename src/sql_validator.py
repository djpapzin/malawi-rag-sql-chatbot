"""
SQL Validation Module

This module provides SQL validation using LangChain's built-in validators and custom validators
for the Malawi infrastructure projects database.
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_community.utilities import SQLDatabase
from langchain_community.chains.sql_database import SQLDatabaseChain
from langchain_community.chains.sql_database.query_checker import check_sql_query
import sqlparse
import re
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    BASIC = "basic"  # Basic syntax and injection checks
    STRICT = "strict"  # Additional semantic validation
    FULL = "full"  # Complete validation including performance checks

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    query: Optional[str] = None  # Potentially modified/cleaned query

class SQLValidator:
    """SQL Validator using LangChain and custom validation rules"""
    
    def __init__(self, db: SQLDatabase, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.db = db
        self.validation_level = validation_level
        self.allowed_tables = ["proj_dashboard"]
        self.allowed_columns = {
            "proj_dashboard": [
                "PROJECTNAME", "PROJECTCODE", "FISCALYEAR", "REGION", "DISTRICT",
                "TOTALBUDGET", "PROJECTSTATUS", "PROJECTSECTOR", "CONTRACTORNAME",
                "STARTDATE", "TOTALEXPENDITURETODATE", "FUNDINGSOURCE", "LASTVISIT"
            ]
        }
        
    def validate_query(self, query: str) -> ValidationResult:
        """
        Validate an SQL query using multiple validation steps
        
        Args:
            query (str): The SQL query to validate
            
        Returns:
            ValidationResult: Result of validation including any errors or warnings
        """
        errors = []
        warnings = []
        modified_query = query
        
        # Basic validation (always performed)
        basic_result = self._basic_validation(modified_query)
        errors.extend(basic_result.errors)
        warnings.extend(basic_result.warnings)
        modified_query = basic_result.query or modified_query
        
        if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.FULL]:
            # Strict validation
            strict_result = self._strict_validation(modified_query)
            errors.extend(strict_result.errors)
            warnings.extend(strict_result.warnings)
            modified_query = strict_result.query or modified_query
            
        if self.validation_level == ValidationLevel.FULL:
            # Full validation including performance checks
            full_result = self._full_validation(modified_query)
            errors.extend(full_result.errors)
            warnings.extend(full_result.warnings)
            modified_query = full_result.query or modified_query
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            query=modified_query
        )
    
    def _basic_validation(self, query: str) -> ValidationResult:
        """Basic SQL validation including syntax and injection checks"""
        errors = []
        warnings = []
        
        # Check for empty query
        if not query or not query.strip():
            return ValidationResult(False, ["Empty query"], [], None)
        
        # Remove comments and clean whitespace
        cleaned_query = sqlparse.format(query, strip_comments=True).strip()
        
        try:
            # Parse the query
            parsed = sqlparse.parse(cleaned_query)
            if not parsed:
                return ValidationResult(False, ["Failed to parse SQL query"], [], None)
            
            # Check for basic SQL injection patterns
            injection_patterns = [
                r';\s*DROP\s+TABLE',
                r';\s*DELETE\s+FROM',
                r';\s*UPDATE\s+\w+\s+SET',
                r';\s*INSERT\s+INTO',
                r'--',
                r'/\*.*?\*/',
                r'UNION\s+ALL\s+SELECT',
                r'UNION\s+SELECT'
            ]
            
            for pattern in injection_patterns:
                if re.search(pattern, cleaned_query, re.IGNORECASE):
                    errors.append(f"Potential SQL injection detected: {pattern}")
            
            # Validate basic query structure
            if not cleaned_query.lower().startswith('select'):
                errors.append("Query must start with SELECT")
                
            if 'proj_dashboard' not in cleaned_query.lower():
                errors.append("Query must reference proj_dashboard table")
                
        except Exception as e:
            errors.append(f"SQL parsing error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            query=cleaned_query
        )
    
    def _strict_validation(self, query: str) -> ValidationResult:
        """Strict validation including semantic checks"""
        errors = []
        warnings = []
        modified_query = query
        
        try:
            # Use LangChain's query checker
            check_result = check_sql_query(query, self.db)
            if not check_result['valid']:
                errors.append(f"LangChain validation failed: {check_result['error']}")
            
            # Parse and validate table/column references
            parsed = sqlparse.parse(query)[0]
            
            # Extract table references
            tables = set()
            for token in parsed.flatten():
                if token.ttype is None and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:
                        tables.add(token.value.split('.')[0])
            
            # Validate table references
            for table in tables:
                if table.lower() not in [t.lower() for t in self.allowed_tables]:
                    errors.append(f"Invalid table reference: {table}")
            
            # Extract and validate column references
            columns = set()
            for token in parsed.flatten():
                if token.ttype is None and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:
                        columns.add(token.value.split('.')[1])
                    else:
                        columns.add(token.value)
            
            # Check column validity
            valid_columns = set(col.lower() for col in self.allowed_columns["proj_dashboard"])
            for col in columns:
                if col.lower() not in valid_columns and col != '*':
                    errors.append(f"Invalid column reference: {col}")
            
            # Check for proper WHERE clause
            if 'where' not in query.lower():
                warnings.append("Query missing WHERE clause - might return too many results")
            
            # Check for LIMIT clause
            if 'limit' not in query.lower():
                warnings.append("Query missing LIMIT clause")
                modified_query = f"{query.rstrip(';')} LIMIT 1000;"
            
        except Exception as e:
            errors.append(f"Strict validation error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            query=modified_query
        )
    
    def _full_validation(self, query: str) -> ValidationResult:
        """Full validation including performance checks"""
        errors = []
        warnings = []
        
        try:
            # Check for performance issues
            parsed = sqlparse.parse(query)[0]
            
            # Check for SELECT *
            if any(token.value == '*' for token in parsed.flatten()):
                warnings.append("Using SELECT * is not recommended for performance")
            
            # Check for missing indexes in WHERE clause
            where_clause = None
            for token in parsed.flatten():
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'WHERE':
                    where_clause = token.parent
                    break
            
            if where_clause:
                # Add warnings for non-indexed columns in WHERE clause
                # This is a placeholder - in a real implementation, we would check actual DB indexes
                pass
            
            # Check for proper ORDER BY with LIMIT
            has_order_by = 'order by' in query.lower()
            has_limit = 'limit' in query.lower()
            
            if has_limit and not has_order_by:
                warnings.append("Using LIMIT without ORDER BY may lead to inconsistent results")
            
            # Check for potential cartesian products
            if query.lower().count('join') > 0 and 'where' not in query.lower():
                warnings.append("JOIN without WHERE clause may cause cartesian product")
            
        except Exception as e:
            errors.append(f"Performance validation error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            query=query
        ) 