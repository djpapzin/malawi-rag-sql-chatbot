# Query Response Patterns in Dziwani Chatbot

This document explains how the chatbot determines what type of query is being asked and how it should format its responses accordingly.

## Types of Queries and Response Patterns

### 1. General Queries
   
**Definition**: Queries that refer to multiple projects or a category of projects.

**Examples**:
- "Show me all education projects in Lilongwe"
- "List health sector projects"
- "What projects are happening in Zomba district?"

**Response Pattern**: 
- Display a list of multiple projects
- For each project, show the 6 basic fields
- Include pagination information if applicable

```
Found 15 education projects in Lilongwe, showing first 10:

1. Lilongwe Primary School Renovation
   - Fiscal year: 2023-2024
   - Location: Lilongwe
   - Budget: MWK 120,000,000
   - Status: In progress
   - Project Sector: Education

2. Kamuzu Institute Library Expansion
   - Fiscal year: 2022-2023
   - Location: Lilongwe
   - Budget: MWK 85,000,000
   - Status: Completed
   - Project Sector: Education

...and so on
```

### 2. Specific Project Queries

**Definition**: Queries that specifically ask about one project, either by name or by unique identifying characteristics.

**Examples**:
- "Tell me about the Lilongwe Primary School Renovation"
- "Show details of the Zomba District Hospital construction"
- "What is the status of the M1 Road rehabilitation project?"

**Response Pattern**:
- Display comprehensive information about a single project
- Show all 12 required fields
- Format information in a clear, structured way

```
Details for Lilongwe Primary School Renovation:

- Name: Lilongwe Primary School Renovation
- Fiscal year: 2023-2024
- Location: Lilongwe
- Budget: MWK 120,000,000
- Status: In progress
- Contractor name: Malawi Construction Ltd.
- Contract start date: May 15, 2023
- Expenditure to date: MWK 75,000,000
- Sector: Education
- Source of funding: World Bank Education Grant
- Project code: EDU-LLW-2023-005
- Date of last Council monitoring visit: January 12, 2024
```

### 3. Follow-up Questions

**Definition**: Questions that refer to a previously discussed project without naming it explicitly.

**Examples**:
- "Is it complete?"
- "When did construction start?"
- "How much of the budget has been spent?"
- "Who is the contractor?"

**Response Pattern**:
- Provide a direct answer to the specific question
- Reference relevant field(s) from the project data
- Keep the response conversational and natural
- Do not re-list all fields unless specifically asked

```
No, the Lilongwe Primary School Renovation is still in progress. According to the latest data, it's 62% complete with an expected completion date of August 2024.
```

## How the System Determines Query Type

### Intent Recognition
The system uses several methods to determine query intent:

1. **Named Entity Recognition**: If a specific project name is mentioned, the query is likely a specific project query.

2. **Question Context**:
   - Questions with plural terms like "all projects," "which projects," etc. suggest general queries
   - Questions with specific identifiers like "tell me about the [project name]" indicate specific queries
   - Brief questions without project identifiers that follow a specific query are likely follow-up questions

3. **Conversation History**:
   - If a specific project was just discussed, a short follow-up question is assumed to be about that same project
   - If the user asks a new question with different parameters (location, sector, etc.), it's treated as a new general query

### Technical Implementation of Intent Recognition

The Dziwani chatbot uses a **hybrid approach** for intent recognition, combining the strengths of both rule-based patterns and LLM capabilities:

1. **Initial LLM Classification**:
   - The user's query is first sent to the LLM for high-level intent classification
   - The LLM identifies whether the query is likely general, specific, or a follow-up
   - This leverages the LLM's sophisticated understanding of natural language and context

2. **Rule-Based Verification**:
   - After the LLM classification, rule-based checks are applied to verify the classification
   - Regular expressions identify key patterns like:
     - Plural terms ("projects", "all", "which") for general queries
     - Project name mentions for specific queries
     - Brief questions following a specific query for follow-ups
   - These rules act as a safety net to catch cases where the LLM might misinterpret

3. **Contextual Analysis**:
   - The conversation history is maintained in the session
   - Recent mentions of specific projects are tracked
   - Query length and structure are analyzed (short queries following specific queries are likely follow-ups)

4. **Confidence Scoring**:
   - Each approach (LLM and rule-based) provides a confidence score
   - The final decision combines these scores, with higher weights given to the LLM for complex queries
   - If confidence is below a threshold, clarification is requested from the user

This hybrid approach combines the nuanced understanding of the LLM with the reliability of explicit rules, resulting in more accurate intent recognition than either method alone would provide.

### Implementation Approach

The system maintains a conversation context that tracks:

1. **Current project focus**: If a specific project has been identified in the conversation
2. **Last query type**: Whether the last query was general or specific
3. **Available context fields**: Which fields of the current project have already been discussed

When determining response format:

```
if (query contains specific project name or ID):
    return specific_project_response(project)
else if (query contains plural indicators OR contains filter terms like "in [location]" or "[sector] sector"):
    return general_query_response(filtered_projects)
else if (conversation_has_current_project AND query is brief):
    return followup_response(current_project, query)
else:
    return clarification_response()
```

## Edge Cases and Handling

### Ambiguous Queries
For queries that could be interpreted multiple ways, the system should:
1. Make its best guess based on available context
2. Potentially include clarifying information in the response
3. Be prepared to refine results if the user provides feedback

### Switching Between Projects
If a user has been discussing Project A and then mentions Project B:
1. The system should recognize this as a new specific query
2. Reset the conversation focus to Project B
3. Provide the full specific project response for Project B

### Clarification Requests
If the system cannot determine the query intent:

```
I'm not sure which project you're asking about. Could you provide more details or the name of the specific project you're interested in?
```

## Summary

By correctly identifying query intent, the Dziwani chatbot can provide appropriately formatted responses:
- Comprehensive lists for general queries
- Detailed information for specific project queries
- Direct, conversational answers for follow-up questions

This creates a natural interaction pattern that gives users the information they need in the most appropriate format for each situation. 