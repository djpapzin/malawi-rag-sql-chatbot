# Query Classification Improvement Plan

## Current Query Classification System

### How the System Currently Differentiates Between Query Types

The Dziwani chatbot currently uses a rule-based approach with regex patterns to classify queries into different types:

#### 1. General Queries
- **Detection Method**: Uses regex patterns to match keywords related to sectors, districts, etc.
- **Example Patterns**:
  - `r'(?:show|list|tell me about|what are)(?: the)? (?:all )?(?:projects|infrastructure)(?: projects)? in (?:the )?([a-zA-Z\s]+) (?:district|region)'`
  - `r'(?:show|list|tell me about|what are)(?: the)? (?:all )?([a-zA-Z\s]+) (?:sector|type) projects'`
- **Response Format**: Returns a list of projects with basic information

#### 2. Specific Project Queries
- **Detection Method**: Uses regex to identify requests for specific project details
- **Example Pattern**: `r'(?:about|tell me about|information on|details of|details about)(?: the)? ([a-zA-Z0-9\s\-]+?)(?:\s+project|\s*$)'`
- **Response Format**: Returns detailed information about a single project in card format

#### 3. Out-of-Context Queries
- **Detection Method**: Default fallback when no patterns match
- **Response Format**: Generic response or attempt to provide general information

### Limitations of the Current Approach

1. **Rigid Pattern Matching**: Relies heavily on predefined regex patterns that can't adapt to variations in user queries
2. **Limited Context Understanding**: Cannot understand the relationship between consecutive queries
3. **No Memory of Previous Interactions**: Each query is processed independently without considering conversation history
4. **Difficulty with Drill-Down Queries**: Struggles to recognize when a user wants details about a project mentioned in a previous response
5. **Binary Classification**: Queries are either matched or not matched, with no nuance in between

## Proposed Improvement Plan: LLM-Based Query Classification

### 1. Leverage LLM for Query Classification

Instead of relying solely on regex patterns, we can use the LLM to classify queries:

```python
def classify_query(user_query, conversation_history):
    """
    Use the LLM to classify the query type based on the query and conversation history
    """
    prompt = f"""
    Given the following conversation history and the current user query, classify the query into one of these categories:
    1. GENERAL_QUERY: User is asking about multiple projects or categories
    2. SPECIFIC_PROJECT_QUERY: User is asking about a specific project
    3. DRILL_DOWN_QUERY: User is asking for more details about something mentioned earlier
    4. OUT_OF_CONTEXT: Query is unrelated to infrastructure projects
    
    Conversation history:
    {conversation_history}
    
    Current query: {user_query}
    
    Classification:
    """
    
    response = llm(prompt)
    return response.strip()
```

### 2. Maintain Conversation Context

Implement a conversation history tracker to provide context for query classification:

```python
class ConversationTracker:
    def __init__(self, max_history=5):
        self.history = []
        self.max_history = max_history
        self.mentioned_projects = set()
    
    def add_exchange(self, user_query, system_response):
        self.history.append({"user": user_query, "system": system_response})
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Extract project names from the response
        self._extract_project_names(system_response)
    
    def _extract_project_names(self, response):
        # Logic to extract project names from response
        # Add to self.mentioned_projects
        pass
    
    def get_formatted_history(self):
        return "\n".join([f"User: {exchange['user']}\nSystem: {exchange['system']}" for exchange in self.history])
    
    def is_project_mentioned(self, project_name):
        # Check if a project was mentioned in previous exchanges
        return any(project_name.lower() in project.lower() for project in self.mentioned_projects)
```

### 3. Enhanced Query Processing Pipeline

Implement a more sophisticated query processing pipeline:

```python
async def process_query(self, user_query):
    # Add the query to conversation history
    conversation_history = self.conversation_tracker.get_formatted_history()
    
    # Use LLM to classify the query
    query_type = await self.classify_query(user_query, conversation_history)
    
    if query_type == "GENERAL_QUERY":
        return await self.handle_general_query(user_query)
    elif query_type == "SPECIFIC_PROJECT_QUERY":
        project_name = await self.extract_project_name(user_query, conversation_history)
        return await self.handle_specific_project_query(project_name)
    elif query_type == "DRILL_DOWN_QUERY":
        project_name = await self.extract_project_from_context(user_query, conversation_history)
        return await self.handle_specific_project_query(project_name)
    else:  # OUT_OF_CONTEXT
        return await self.handle_out_of_context_query(user_query)
```

### 4. Project Name Extraction with LLM

Use the LLM to extract project names from queries and conversation context:

```python
async def extract_project_from_context(self, user_query, conversation_history):
    prompt = f"""
    Given the following conversation history and the current user query, identify which specific project the user is asking about.
    
    Conversation history:
    {conversation_history}
    
    Current query: {user_query}
    
    Project name:
    """
    
    response = await self.llm(prompt)
    return response.strip()
```

### 5. Implementation Phases

#### Phase 1: Conversation History Tracking
- Implement the ConversationTracker class
- Modify the process_query method to maintain conversation history
- Test with simple follow-up queries

#### Phase 2: LLM-Based Query Classification
- Implement the classify_query method
- Integrate with the existing process_query pipeline
- Test with a variety of query types

#### Phase 3: Context-Aware Project Name Extraction
- Implement the extract_project_from_context method
- Test with drill-down queries
- Fine-tune the extraction logic

#### Phase 4: Response Format Selection
- Modify the response generation to select the appropriate format based on query type
- Ensure drill-down queries use the card-style format for project details

## Benefits of the Proposed Approach

1. **Better Context Understanding**: The LLM can understand the relationship between queries in a conversation
2. **More Flexible Query Recognition**: No need for rigid regex patterns to match every possible query variation
3. **Improved Drill-Down Handling**: System can recognize when a user wants more details about a previously mentioned project
4. **Natural Conversation Flow**: Users can interact more naturally without having to format their queries in specific ways
5. **Adaptability**: The system can adapt to new query patterns without code changes

## Challenges and Considerations

1. **Latency**: LLM-based classification may introduce additional latency
2. **Cost**: More LLM calls will increase API usage costs
3. **Reliability**: LLM responses may be inconsistent; robust error handling is needed
4. **Fallback Mechanisms**: Should maintain regex patterns as fallbacks when LLM classification fails

## Next Steps

1. Implement a prototype of the conversation tracker
2. Test LLM-based query classification with sample conversations
3. Compare performance against the current regex-based approach
4. Gradually replace regex patterns with LLM-based classification
5. Monitor system performance and user satisfaction

## Implementation Checklist

### Phase 1: Setup and Preparation
- [ ] Review current codebase and identify all places where regex-based query classification is used
- [ ] Create a new module for conversation tracking (`conversation_tracker.py`)
- [ ] Define metrics to measure improvement (accuracy of classification, user satisfaction)
- [ ] Create test dataset of sample queries and conversations for testing
- [ ] Set up logging for query classification results

### Phase 2: Conversation History Tracking
- [ ] Implement `ConversationTracker` class with the following methods:
  - [ ] `add_exchange()` - Store user query and system response
  - [ ] `get_formatted_history()` - Format conversation for LLM context
  - [ ] `extract_project_names()` - Identify project names in responses
- [ ] Modify the main query handler to instantiate and maintain the conversation tracker
- [ ] Add conversation history to the context passed to query processing functions
- [ ] Add unit tests for conversation tracking
- [ ] Test with sample conversations to ensure history is properly maintained

### Phase 3: LLM-Based Query Classification
- [ ] Create prompt templates for query classification
- [ ] Implement `classify_query()` function using the LLM
- [ ] Create fallback mechanism for when LLM classification fails
- [ ] Modify the query processing pipeline to use LLM classification
- [ ] Implement caching for similar queries to reduce latency and costs
- [ ] Add logging to compare LLM classification vs. regex classification
- [ ] Test with various query types to measure accuracy improvement

### Phase 4: Context-Aware Project Name Extraction
- [ ] Create prompt templates for project name extraction
- [ ] Implement `extract_project_from_context()` function
- [ ] Enhance project mention tracking in `ConversationTracker`
- [ ] Update query handlers to use context-aware project extraction
- [ ] Add tests for project name extraction with different conversation contexts
- [ ] Test with drill-down queries to measure accuracy

### Phase 5: Response Format Selection
- [ ] Update response generators to select format based on query type
- [ ] Ensure drill-down queries use card-style format for project details
- [ ] Create unified response formatting logic for all query types
- [ ] Test with end-to-end conversation flows

### Phase 6: Integration and Optimization
- [ ] Gradually replace regex patterns with LLM-based classification
- [ ] Optimize prompts to reduce token usage and latency
- [ ] Implement parallel processing where possible
- [ ] Add comprehensive error handling
- [ ] Create graceful degradation paths when LLM is unavailable

### Phase 7: Testing and Validation
- [ ] Conduct A/B testing with both classification methods
- [ ] Gather metrics on:
  - [ ] Classification accuracy
  - [ ] Response relevance
  - [ ] Processing time
  - [ ] User satisfaction
- [ ] Fix any issues identified during testing
- [ ] Document performance improvements

### Phase 8: Deployment and Monitoring
- [ ] Deploy to staging environment
- [ ] Conduct user acceptance testing
- [ ] Deploy to production
- [ ] Monitor system performance
- [ ] Establish feedback loop for continuous improvement

### Success Criteria
- [ ] At least 95% accuracy in query classification
- [ ] Proper handling of at least 90% of drill-down queries
- [ ] No increase in average response time greater than 20%
- [ ] Positive user feedback on conversation naturalness
- [ ] Reduced need for users to rephrase their questions
