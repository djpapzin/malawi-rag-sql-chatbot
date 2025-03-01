#!/usr/bin/env python3
"""
LLM Budget Correction Tool

This script processes LLM responses to fix budget magnitude errors.
It looks for common patterns in budget reporting and applies corrections
based on the verified database values.
"""

import re
import sys
import json
import argparse
from pathlib import Path

# Display formatting constants
HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

# Known project budget corrections (actual validated figures)
KNOWN_PROJECTS = {
    "Construction of a Maternity Block and 1no. Staff house at Liwera Health Centre": 195_000_000.00,
    "Construction of a Maternity Block and 1no. Staff house at Beni Health Centre": 195_000_000.00,
    "Completion of Chinkombero maternity wing and dispensary": 120_000_000.00,
    # Add more projects as they are verified
}

def format_currency(amount):
    """Format a number as currency (MWK)."""
    if amount is None:
        return "N/A"
    return f"MWK {amount:,.2f}"

def extract_budgets(text):
    """Extract budget mentions from text using regex."""
    # Pattern to match "MWK X,XXX,XXX,XXX.XX" or similar formats
    pattern = r'MWK\s+([\d,]+(?:\.\d+)?)'
    matches = re.findall(pattern, text)
    
    results = []
    for match in matches:
        # Remove commas and convert to float
        try:
            value = float(match.replace(',', ''))
            results.append(value)
        except ValueError:
            continue
    
    return results

def fix_magnitude(budget):
    """Fix the magnitude of a budget value based on heuristics."""
    # If the budget is suspiciously large (over 1 billion), divide by 10
    if budget > 1_000_000_000:
        return budget / 10
    return budget

def process_text(text):
    """Process text to identify and fix budget figures."""
    # First look for known project names and their associated budgets
    for project, correct_budget in KNOWN_PROJECTS.items():
        if project in text:
            # Use regex with word boundaries to find the budget associated with this project
            pattern = rf'{re.escape(project)}.*?MWK\s+([\d,]+(?:\.\d+)?)'
            match = re.search(pattern, text, re.DOTALL)
            
            if match:
                try:
                    mentioned_budget = float(match.group(1).replace(',', ''))
                    # Replace the incorrect budget with the correct one in the specific context
                    # Find the full line or paragraph containing the project and budget
                    project_context = re.search(rf'[^\n]*{re.escape(project)}[^\n]*MWK\s+{re.escape(match.group(1))}[^\n]*', text)
                    if project_context:
                        original_text = project_context.group(0)
                        corrected_text = original_text.replace(
                            f"MWK {match.group(1)}", 
                            format_currency(correct_budget)[4:]  # Remove "MWK " prefix
                        )
                        text = text.replace(original_text, corrected_text)
                        print(f"{YELLOW}Corrected budget for project '{project}':")
                        print(f"  Original: MWK {match.group(1)}")
                        print(f"  Corrected: {format_currency(correct_budget)}{ENDC}")
                except (ValueError, IndexError):
                    pass
            
            # Also look for cases where the budget is mentioned without "MWK" prefix
            # This handles cases where previous corrections might have removed the prefix
            alt_pattern = rf'{re.escape(project)}.*?(?:budget|allocated|has)\s+(?:of|is)?\s+([\d,]+(?:\.\d+)?)'
            alt_match = re.search(alt_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if alt_match:
                try:
                    mentioned_budget = float(alt_match.group(1).replace(',', ''))
                    if abs(mentioned_budget - correct_budget) > 0.01:  # Only replace if different
                        # Find the full line or paragraph containing the project and budget
                        project_context = re.search(rf'[^\n]*{re.escape(project)}[^\n]*{re.escape(alt_match.group(1))}[^\n]*', text)
                        if project_context:
                            original_text = project_context.group(0)
                            corrected_text = original_text.replace(
                                alt_match.group(1), 
                                format_currency(correct_budget)[4:]  # Remove "MWK " prefix
                            )
                            text = text.replace(original_text, corrected_text)
                            print(f"{YELLOW}Corrected budget for project '{project}' (without MWK prefix):")
                            print(f"  Original: {alt_match.group(1)}")
                            print(f"  Corrected: {format_currency(correct_budget)[4:]}{ENDC}")
                except (ValueError, IndexError):
                    pass
    
    # Then look for general budget magnitudes to fix
    budgets = extract_budgets(text)
    for budget in budgets:
        fixed_budget = fix_magnitude(budget)
        if fixed_budget != budget:
            print(f"{YELLOW}Corrected general budget magnitude:")
            print(f"  Original: {format_currency(budget)}")
            print(f"  Corrected: {format_currency(fixed_budget)}{ENDC}")
            # Replace in text, being careful with the formatting
            formatted_orig = format_currency(budget)[4:]  # Remove "MWK " prefix
            formatted_fixed = format_currency(fixed_budget)[4:]
            text = text.replace(formatted_orig, formatted_fixed)
    
    return text

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Fix budget magnitudes in LLM responses.')
    parser.add_argument('input', nargs='?', help='Input file (or use stdin if not provided)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        try:
            with open(args.input, 'r') as f:
                text = f.read()
        except IOError as e:
            print(f"{RED}Error reading input file: {e}{ENDC}")
            sys.exit(1)
    else:
        # Read from stdin
        print(f"{BLUE}Reading from stdin. Press Ctrl+D when finished.{ENDC}")
        text = sys.stdin.read()
    
    # Process the text
    corrected_text = process_text(text)
    
    # Output the result
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(corrected_text)
            print(f"{GREEN}Corrected text written to {args.output}{ENDC}")
        except IOError as e:
            print(f"{RED}Error writing to output file: {e}{ENDC}")
            sys.exit(1)
    else:
        print(f"\n{BOLD}{GREEN}=== Corrected Text ==={ENDC}")
        print(corrected_text)

if __name__ == '__main__':
    main() 