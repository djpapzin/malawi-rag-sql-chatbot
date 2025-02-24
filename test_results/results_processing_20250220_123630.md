# Test Results: results_processing

Generated: 2025-02-20 12:36:30

## Summary

- Total Tests: 2
- Passed: 2
- Failed: 0
- Execution Time: 1.54 seconds

## Test Cases

### Results Processing Test Case 1

**Description**: Testing results processing for: How many projects are there?

**Test Data**:
```python
{'question': 'How many projects are there?', 'query': 'SELECT COUNT(*) as count FROM proj_dashboard;', 'results': [(42,)], 'expected_keywords': ['42', 'projects']}
```

**Actual Results**:
```
There are 42 projects.
```

**Status**: ✅ PASSED

### Results Processing Test Case 2

**Description**: Testing results processing for: What is the total budget?

**Test Data**:
```python
{'question': 'What is the total budget?', 'query': 'SELECT SUM(budget) as total FROM proj_dashboard;', 'results': [(1000000,)], 'expected_keywords': ['1000000', 'budget', 'total']}
```

**Actual Results**:
```
The total budget is 1000000.
```

**Status**: ✅ PASSED

