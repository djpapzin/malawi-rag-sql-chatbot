# LangChain Integration Plan

This document outlines the specific steps needed to integrate our LLM-driven approach with the existing LangChain SQL implementation in the Dziwani chatbot.

## Current Implementation Analysis

The current implementation uses:

1. **Together AI API** directly for LLM interactions
2. **Custom DatabaseManager** for SQLite operations
3. **Basic intent detection** with regex patterns
4. **Manual SQL extraction** from LLM responses
5. **Hard-coded response formatting** in ResponseGenerator

## Integration Strategy

### Phase 1: Non-Invasive Enhancements (1-2 days)

These changes can be implemented without disrupting the current functionality:

- [ ] **Enhanced Intent Detection**
  - Implement LLM-based intent analysis in parallel with existing detection
  - Compare results and use as fallback
  - Gradually transition to LLM-based approach

- [ ] **Response Formatting Improvements**
  - Add dynamic field ordering based on query context
  - Implement smarter formatting rules
  - Keep compatibility with existing response structure

### Phase 2: SQL Generation Enhancements (2-3 days)

- [ ] **Schema-Aware Prompting**
  - Extract database schema using existing methods
  - Enhance prompts with schema context
  - Improve SQL generation with better context

- [ ] **Query Validation Layer**
  - Add validation for generated SQL
  - Implement error correction for common issues
  - Create fallback to simpler queries when needed

### Phase 3: Full LangChain Integration (3-4 days)

- [ ] **SQLDatabase Wrapper**
  - Create LangChain SQLDatabase wrapper around existing connection
  - Implement table_info and run_query methods
  - Maintain compatibility with current implementation

- [ ] **Chain Integration**
  - Implement SQLDatabaseChain with custom prompts
  - Add result post-processing for Malawi-specific formatting
  - Create hybrid approach that leverages both implementations

### Phase 4: Migration Strategy (2-3 days)

- [ ] **Feature Flags**
  - Add configuration for toggling between implementations
  - Implement A/B testing capabilities
  - Create metrics for comparing approaches

- [ ] **Gradual Transition**
  - Start with non-critical query types
  - Monitor performance and accuracy
  - Expand to more complex queries

## Implementation Details

### 1. LangChain SQLDatabase Integration

```python
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

# Create a wrapper around the existing database connection
def create_langchain_db():
    # Get existing connection string
    connection_string = "sqlite:///path/to/database.db"
    
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)
    
    # Create LangChain SQLDatabase
    db = SQLDatabase(engine)
    
    return db
```

### 2. Enhanced SQL Generation

```python
from langchain.chains import SQLDatabaseChain
from langchain_openai import ChatOpenAI

def generate_sql_with_langchain(query, db):
    # Initialize LLM
    llm = ChatOpenAI(temperature=0.1)
    
    # Create chain
    db_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=db,
        verbose=True,
        return_intermediate_steps=True
    )
    
    # Run chain
    result = db_chain.invoke(query)
    
    return {
        "sql": result["intermediate_steps"][0],
        "result": result["result"]
    }
```

### 3. Hybrid Approach Implementation

```python
def process_query(query):
    # Detect intent
    intent = detect_intent(query)
    
    if intent == "SPECIFIC":
        # Try LangChain approach first
        try:
            db = create_langchain_db()
            result = generate_sql_with_langchain(query, db)
            return format_response(result)
        except Exception as e:
            logger.warning(f"LangChain approach failed: {str(e)}")
            # Fall back to existing implementation
            return existing_process_query(query)
    else:
        # Use existing implementation for non-SQL intents
        return existing_process_query(query)
```

## Testing Strategy

1. **Unit Tests**
   - Test SQL generation with various query types
   - Validate response formatting
   - Check error handling

2. **Integration Tests**
   - End-to-end tests with real database
   - Compare results between implementations
   - Measure performance differences

3. **Evaluation Metrics**
   - SQL correctness (does it retrieve the right data?)
   - Response quality (is the information presented well?)
   - Performance (how long does it take?)
   - Error rate (how often does it fail?)

## Rollout Plan

1. **Development Environment**
   - Implement and test all changes
   - Compare results with existing implementation

2. **Staging Environment**
   - Deploy to http://154.0.164.254:5000
   - Run comprehensive tests
   - Gather metrics

3. **Production**
   - Gradual rollout with feature flags
   - Monitor performance and user feedback
   - Expand to more query types over time

## Success Criteria

- Equal or better SQL generation accuracy
- Improved response quality and relevance
- Reduced need for hard-coding
- Maintainable and extensible architecture
