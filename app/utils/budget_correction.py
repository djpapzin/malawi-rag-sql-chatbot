"""
Budget Correction Utility

This module provides functions to correct budget magnitudes in LLM responses
before they are sent to the user.
"""

import re
import sys
import os
from pathlib import Path

# Add the scripts directory to the path so we can import the fix_llm_budget module
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.append(str(scripts_dir))

try:
    from fix_llm_budget import process_text, KNOWN_PROJECTS
except ImportError:
    # Fallback implementation if the import fails
    def process_text(text):
        """Fallback implementation that just returns the original text."""
        return text
    
    KNOWN_PROJECTS = {}

def correct_budget_in_response(llm_response):
    """
    Apply budget corrections to an LLM response.
    
    Args:
        llm_response (str): The text response from the LLM
        
    Returns:
        str: The corrected response with fixed budget figures
    """
    # Skip correction if the response doesn't contain budget information
    if "MWK" not in llm_response and "budget" not in llm_response.lower():
        return llm_response
    
    try:
        # Process the text to correct budget figures
        corrected_response = process_text(llm_response)
        return corrected_response
    except Exception as e:
        # Log the error but return the original response to avoid breaking the application
        print(f"Error correcting budget in LLM response: {e}", file=sys.stderr)
        return llm_response

def get_known_project_budgets():
    """
    Get a dictionary of known project budgets for reference.
    
    Returns:
        dict: A dictionary mapping project names to their verified budgets
    """
    return KNOWN_PROJECTS.copy()

def add_known_project_budget(project_name, budget):
    """
    Add a new verified project budget to the known projects.
    
    Args:
        project_name (str): The exact project name
        budget (float): The verified budget amount
    """
    KNOWN_PROJECTS[project_name] = budget 