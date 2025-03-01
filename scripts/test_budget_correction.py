#!/usr/bin/env python3
"""
Test Budget Correction Integration

This script tests the budget correction integration by simulating LLM responses
with budget errors and verifying that they are corrected properly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the budget correction utility
from app.utils.budget_correction import correct_budget_in_response, get_known_project_budgets

# Test cases with incorrect budget figures
TEST_CASES = [
    {
        "name": "Health sector budget",
        "input": "The total budget for health sector projects is MWK 13,044,625,236.90, which is allocated across 43 different projects.",
        "expected_contains": "1,304,462,523.69"
    },
    {
        "name": "Liwera Health Centre",
        "input": "The Construction of a Maternity Block and 1no. Staff house at Liwera Health Centre has a budget of MWK 1,950,000,000.00.",
        "expected_contains": "195,000,000.00"
    },
    {
        "name": "Beni Health Centre",
        "input": "Another significant project is the Construction of a Maternity Block and 1no. Staff house at Beni Health Centre, which has been allocated MWK 1,950,000,000.00.",
        "expected_contains": "195,000,000.00"
    },
    {
        "name": "Chinkombero maternity wing",
        "input": "The Completion of Chinkombero maternity wing and dispensary project has a budget of MWK 1,200,000,000.00.",
        "expected_contains": "120,000,000.00"
    }
]

def run_tests():
    """Run all test cases and report results"""
    print(f"Known project budgets: {get_known_project_budgets()}")
    print("\nRunning budget correction tests...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Input: {test['input']}")
        
        # Apply correction
        corrected = correct_budget_in_response(test['input'])
        print(f"  Output: {corrected}")
        
        # Check if correction was applied correctly
        if test['expected_contains'] in corrected:
            print(f"  Result: ✅ PASSED")
            passed += 1
        else:
            print(f"  Result: ❌ FAILED - Expected to contain '{test['expected_contains']}'")
            failed += 1
        
        print()
    
    # Print summary
    print(f"Test Summary: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(1 if failed > 0 else 0) 