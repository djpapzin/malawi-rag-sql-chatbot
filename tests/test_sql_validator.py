import pytest
from src.sql_validator import SQLValidator, ValidationLevel, ValidationResult
from langchain_community.utilities import SQLDatabase
from unittest.mock import Mock, patch

@pytest.fixture
def mock_db():
    db = Mock(spec=SQLDatabase)
    return db

@pytest.fixture
def validator(mock_db):
    return SQLValidator(mock_db)

def test_basic_validation(validator):
    """Test basic SQL validation"""
    # Valid query
    result = validator.validate_query(
        "SELECT PROJECTNAME, TOTALBUDGET FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid
    assert not result.errors
    
    # Empty query
    result = validator.validate_query("")
    assert not result.is_valid
    assert "Empty query" in result.errors[0]
    
    # SQL injection attempt
    result = validator.validate_query(
        "SELECT * FROM proj_dashboard; DROP TABLE proj_dashboard;"
    )
    assert not result.is_valid
    assert any("injection" in err.lower() for err in result.errors)
    
    # Invalid table
    result = validator.validate_query(
        "SELECT * FROM invalid_table;"
    )
    assert not result.is_valid
    assert "proj_dashboard" in result.errors[0]

def test_strict_validation(validator):
    """Test strict validation mode"""
    # Missing LIMIT clause
    result = validator.validate_query(
        "SELECT PROJECTNAME FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid  # Should still be valid
    assert "LIMIT" in result.warnings[0]
    assert "LIMIT 1000" in result.query
    
    # Invalid column
    result = validator.validate_query(
        "SELECT invalid_column FROM proj_dashboard;"
    )
    assert not result.is_valid
    assert "Invalid column" in result.errors[0]
    
    # Missing WHERE clause
    result = validator.validate_query(
        "SELECT PROJECTNAME FROM proj_dashboard;"
    )
    assert result.is_valid  # Should still be valid
    assert "WHERE" in result.warnings[0]

def test_full_validation(validator):
    """Test full validation mode with performance checks"""
    validator.validation_level = ValidationLevel.FULL
    
    # SELECT *
    result = validator.validate_query(
        "SELECT * FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid  # Should still be valid
    assert "SELECT *" in result.warnings[0]
    
    # LIMIT without ORDER BY
    result = validator.validate_query(
        "SELECT PROJECTNAME FROM proj_dashboard LIMIT 10;"
    )
    assert result.is_valid
    assert "ORDER BY" in result.warnings[0]

def test_query_modification(validator):
    """Test query modification capabilities"""
    # Add LIMIT clause
    result = validator.validate_query(
        "SELECT PROJECTNAME FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert "LIMIT 1000" in result.query
    
    # Clean comments
    result = validator.validate_query(
        """-- This is a comment
        SELECT PROJECTNAME 
        FROM proj_dashboard -- Another comment
        WHERE DISTRICT = 'Lilongwe';"""
    )
    assert "--" not in result.query
    assert "comment" not in result.query.lower()

def test_injection_patterns(validator):
    """Test SQL injection pattern detection"""
    injection_patterns = [
        "SELECT * FROM proj_dashboard; DROP TABLE proj_dashboard;",
        "SELECT * FROM proj_dashboard; DELETE FROM proj_dashboard;",
        "SELECT * FROM proj_dashboard; UPDATE proj_dashboard SET PROJECTNAME = 'Hacked';",
        "SELECT * FROM proj_dashboard; INSERT INTO proj_dashboard VALUES (1, 'Hack');",
        "SELECT * FROM proj_dashboard -- Drop everything",
        "SELECT * FROM proj_dashboard /* Malicious comment */",
        "SELECT * FROM proj_dashboard UNION SELECT * FROM users;",
        "SELECT * FROM proj_dashboard UNION ALL SELECT * FROM secrets;"
    ]
    
    for pattern in injection_patterns:
        result = validator.validate_query(pattern)
        assert not result.is_valid
        assert any("injection" in err.lower() for err in result.errors)

def test_validation_levels(mock_db):
    """Test different validation levels"""
    # Basic validation
    basic_validator = SQLValidator(mock_db, ValidationLevel.BASIC)
    result = basic_validator.validate_query(
        "SELECT * FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid
    assert not result.warnings  # Basic validation doesn't check for SELECT *
    
    # Strict validation
    strict_validator = SQLValidator(mock_db, ValidationLevel.STRICT)
    result = strict_validator.validate_query(
        "SELECT * FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid
    assert result.warnings  # Should warn about SELECT *
    
    # Full validation
    full_validator = SQLValidator(mock_db, ValidationLevel.FULL)
    result = full_validator.validate_query(
        "SELECT * FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';"
    )
    assert result.is_valid
    assert any("SELECT *" in w for w in result.warnings)
    assert any("performance" in w.lower() for w in result.warnings)

def test_column_validation(validator):
    """Test column name validation"""
    # Valid columns
    result = validator.validate_query("""
        SELECT 
            PROJECTNAME,
            PROJECTCODE,
            FISCALYEAR,
            REGION,
            DISTRICT,
            TOTALBUDGET,
            PROJECTSTATUS,
            PROJECTSECTOR
        FROM proj_dashboard
        WHERE DISTRICT = 'Lilongwe';
    """)
    assert result.is_valid
    assert not result.errors
    
    # Invalid columns
    result = validator.validate_query("""
        SELECT 
            PROJECTNAME,
            invalid_column1,
            another_invalid_column
        FROM proj_dashboard;
    """)
    assert not result.is_valid
    assert len([err for err in result.errors if "Invalid column" in err]) == 2

def test_error_handling(validator):
    """Test error handling for malformed queries"""
    malformed_queries = [
        "SLECT * FROM proj_dashboard;",  # Misspelled SELECT
        "SELECT * FORM proj_dashboard;",  # Misspelled FROM
        "SELECT * FROM proj_dashboard WHERE;",  # Incomplete WHERE clause
        "SELECT * FROM proj_dashboard GROUP;",  # Incomplete GROUP BY
        "SELECT * FROM proj_dashboard ORDER;",  # Incomplete ORDER BY
    ]
    
    for query in malformed_queries:
        result = validator.validate_query(query)
        assert not result.is_valid
        assert result.errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 