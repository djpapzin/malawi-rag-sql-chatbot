# Test Results: column_selection

Generated: 2025-02-20 12:36:33

## Summary

- Total Tests: 3
- Passed: 3
- Failed: 0
- Execution Time: 0.00 seconds

## Test Cases

### Column Selection: Standard Columns

**Description**: Testing column selection for: Show all projects

**Test Data**:
```python
{'name': 'Standard Columns', 'question': 'Show all projects', 'expected_columns': ['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata'], 'unexpected_columns': []}
```

**Actual Results**:
```
['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata']
```

**Status**: ✅ PASSED

### Column Selection: Specific Project Columns

**Description**: Testing column selection for: Show details about MW-123

**Test Data**:
```python
{'name': 'Specific Project Columns', 'question': 'Show details about MW-123', 'expected_columns': ['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata'], 'unexpected_columns': []}
```

**Actual Results**:
```
['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata']
```

**Status**: ✅ PASSED

### Column Selection: Project Code Columns

**Description**: Testing column selection for: Tell me about project 5f0c

**Test Data**:
```python
{'name': 'Project Code Columns', 'question': 'Tell me about project 5f0c', 'expected_columns': ['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata'], 'unexpected_columns': []}
```

**Actual Results**:
```
['projectname', 'district', 'projectsector', 'projectstatus', 'budget', 'completionpercentage', 'startdate', 'completiondata']
```

**Status**: ✅ PASSED

