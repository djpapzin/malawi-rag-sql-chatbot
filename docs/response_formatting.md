# Response Formatting Standards

## Overview
This document outlines the standardized formatting for query responses in the Malawi Infrastructure Projects Chatbot.

## Response Structure
Each query response is structured with the following sections:

1. **Query Results Header**
   - Title: "Query Results"
   - Clear separation between sections using markdown headers

2. **Question Section**
   - Original natural language query
   - Preserves user's exact wording
   - Helps maintain context

3. **SQL Query Section**
   - Formatted SQL query in a code block
   - Syntax highlighting for SQL
   - Shows the actual query executed

4. **Results Section**
   - Markdown table format
   - Standard column set for consistency
   - Empty cells for null values (instead of "N/A")
   - Proper column alignment
   - Currency formatting with "MWK" prefix
   - Percentage formatting with "%" suffix
   - Thousand separators for numerical values

5. **Answer Section**
   - Header: "Project Details:"
   - Bullet-point list format
   - Bold labels for each field
   - Standardized field order:
     * Project Name
     * Fiscal Year
     * Location
     * Budget
     * Status
     * Project Sector
     * Contractor
     * Start Date
     * Expenditure
     * Funding Source
     * Project Code
     * Last Visit

6. **Metadata Section**
   - Generation timestamp
   - Additional context if available

## Table Formatting
- Column headers are properly capitalized
- Alignment markers (---) for each column
- Empty string for null values
- Consistent spacing
- No truncation of long values

## CSV Export Format
- Proper column headers matching database fields
- "N/A" for null values in CSV
- Proper escaping of special characters
- UTF-8 encoding
- Currency formatting preserved
- Percentage formatting preserved

## Field Formatting Standards

### Text Fields
- Original case preserved
- No truncation
- Special characters preserved

### Numerical Fields
- Thousand separators (e.g., 1,234,567)
- Currency prefix where applicable (MWK)
- Percentage suffix where applicable (%)
- No scientific notation

### Date Fields
- Format: "Month DD, YYYY" (e.g., "January 15, 2024")
- Fiscal year format: "April YYYY / March YYYY"

### Location Fields
- Format: "Region, District"
- Original case preserved

### Status Fields
- Original status preserved
- "Not available" for null values

## Error Handling
- Clear error messages
- "No results found" for empty queries
- "Not available" for missing field values
- Empty cells in tables for null values

## Accessibility Considerations
- Clear section headers
- Consistent formatting
- High contrast text
- Screen reader friendly markdown
- Proper table structure

## Implementation Notes
- Implemented in `result_handler.py`
- Uses standard Python string formatting
- Consistent with markdown best practices
- UTF-8 encoding for all outputs
- Handles special characters properly