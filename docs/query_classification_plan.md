# Query Classification Plan

## Overview
The current system is overly complex with too many specific query types and heavy reliance on regex patterns. We need to simplify this to focus on three main query categories and leverage the LLM's natural language understanding capabilities.

## Query Categories

### 1. Unrelated Queries
- Examples: "hello", "how are you", "what can you do"
- Response: Helpful statements about the chatbot's capabilities
- No database query needed
- LLM handles the response directly

### 2. General Queries
- Examples: 
  - "Show me all education projects"
  - "What projects are in Lilongwe?"
  - "List ongoing water projects"
  - "Show me projects by sector"
- Characteristics:
  - Questions about multiple projects
  - Can include filters (district, sector, status)
  - No specific project context
- Processing:
  - LLM extracts relevant filters/parameters
  - Builds appropriate SQL query
  - Returns filtered results

### 3. Specific Project Queries
- Examples:
  - "Tell me about the Lilongwe Water Project"
  - "What's the status of MW-ED-01?"
  - "Show me the budget for the new school project"
  - Follow-up questions about a specific project
- Characteristics:
  - Focus on a single project
  - Can include project code or name
  - Can include follow-up questions about the same project
- Processing:
  - LLM identifies the specific project
  - Maintains context for follow-up questions
  - Builds focused SQL query for the project

## Implementation Plan

### Phase 1: Simplify Classification
1. Update `QueryType` enum to only include:
   ```python
   class QueryType(str, Enum):
       UNRELATED = "unrelated"
       GENERAL = "general"
       SPECIFIC = "specific"
   ```

2. Modify `QueryParameters` to focus on essential fields:
   ```python
   class QueryParameters(BaseModel):
       project_identifier: Optional[str] = None  # For specific queries
       filters: Dict[str, Any] = Field(default_factory=dict)  # For general queries
       context: Dict[str, Any] = Field(default_factory=dict)  # For follow-up questions
   ```

### Phase 2: Enhance LLM Classification
1. Update the LLM prompt to focus on the three main categories
2. Improve context handling for follow-up questions
3. Add conversation history tracking

### Phase 3: Simplify Query Building
1. Create separate query builders for each category
2. Remove complex regex-based classification
3. Focus on natural language understanding

### Phase 4: Testing and Refinement
1. Test with various query types
2. Gather feedback on response quality
3. Fine-tune LLM prompts and parameters

## Benefits
1. Simpler, more maintainable code
2. Better natural language understanding
3. More accurate responses
4. Easier to extend functionality
5. Better handling of follow-up questions

## Next Steps
1. Review and approve this plan
2. Begin implementation of Phase 1
3. Test with sample queries
4. Iterate based on results 