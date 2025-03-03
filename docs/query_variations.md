# Query Variations for District-Based Searches

This document catalogs different ways users might ask for projects in a specific district, noting which query formats work correctly and which need improvement in the RAG-SQL chatbot system.

## District-Based Query Variations

| Query Format | Example | Works Correctly? | Notes |
|--------------|---------|-----------------|-------|
| Show me all projects in [District] district | "Show me all projects in Dowa district" | ✅ Yes | Returns correct district-filtered results |
| Projects in [District] district | "Projects in Dowa district" | ✅ Yes | Returns correct district-filtered results |
| Which projects are in [District]? | "Which projects are in Dowa?" | ❌ No | Returns top 10 projects across all districts |
| List projects in [District] | "List projects in Dowa" | ❌ No | Returns top 10 projects across all districts |
| Projects located in [District] | "Projects located in Dowa" | ❌ No | Returns top 10 projects across all districts |
| What projects are being implemented in [District]? | "What projects are being implemented in Dowa?" | ❌ No | Returns top 10 projects across all districts |
| Tell me about [District] projects | "Tell me about Dowa projects" | ❌ No | Returns a single project with "Dowa" in the name |
| [District] district projects | "Dowa district projects" | ❌ No | Returns top 10 projects across all districts |
| Find projects in [District] | "Find projects in Dowa" | ❓ Not tested | - |
| Give me a list of [District] projects | "Give me a list of Dowa projects" | ❓ Not tested | - |
| What's happening in [District]? | "What's happening in Dowa?" | ❓ Not tested | - |
| [District] development initiatives | "Dowa development initiatives" | ❓ Not tested | - |
| Infrastructure in [District] | "Infrastructure in Dowa" | ❓ Not tested | - |
| Current projects in [District] | "Current projects in Dowa" | ❓ Not tested | - |
| [District] area projects | "Dowa area projects" | ❓ Not tested | - |

## Recommended Improvements

Based on the testing results, the following improvements are recommended to enhance the system's ability to interpret user intent:

1. **Expand District Recognition Patterns**: The system should recognize district names in various query formats, not just when preceded by "Show me all projects in" or followed by "district".

2. **Improve Intent Recognition**: The system should better identify when a user is asking for district-specific projects, even when the query structure varies.

3. **Handle Implicit District Queries**: When a district name appears in the query, the system should prioritize filtering by that district unless other specific filters are clearly indicated.

4. **Add Synonyms for Projects**: Recognize terms like "initiatives", "developments", "works", etc. as synonyms for "projects".

5. **Implement Fuzzy Matching**: Allow for minor spelling variations or typos in district names.

6. **Context Awareness**: Maintain context across multiple queries, so if a user asks about a district and then asks a follow-up question, the district context is preserved.

## Implementation Suggestions

To implement these improvements, consider:

1. **Enhancing the Prompt Engineering**: Modify the prompts used for the LLM to better handle district-based queries.

2. **Pattern Recognition**: Add more patterns to recognize district-based queries in the query classification logic.

3. **SQL Query Templates**: Create specific SQL query templates for district-based searches that can be used regardless of the exact query phrasing.

4. **User Feedback Loop**: Implement a mechanism to learn from user interactions, especially when queries fail to return expected results.

5. **District Entity Recognition**: Implement specific entity recognition for Malawian districts to ensure they're properly identified in queries.

## Additional Query Types to Test

Future testing should include:

1. **Multi-District Queries**: "Compare projects in Dowa and Lilongwe"
2. **District + Sector Queries**: "Health projects in Dowa"
3. **District + Status Queries**: "Completed projects in Dowa"
4. **District + Budget Queries**: "Highest budget projects in Dowa"
5. **Temporal District Queries**: "Projects in Dowa from 2023" 