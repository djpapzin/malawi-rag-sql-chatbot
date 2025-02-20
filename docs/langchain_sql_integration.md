# LangChain SQL Integration Guide

## Setup & Dependencies

```bash
pip install langchain langchain-community python-dotenv together sqlalchemy
```

## Core Components Integration

### 1. Database Connection Setup
```python
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

# Create SQLDatabase instance
db = SQLDatabase.from_uri("sqlite:///malawi_projects1.db")
```

### 2. LLM Configuration
```python
from langchain_community.llms import Together
import os
from dotenv import load_dotenv

load_dotenv()

llm = Together(
    model="togethercomputer/llama-2-70b-chat",
    together_api_key=os.getenv("TOGETHER_API_KEY"),
    temperature=0.7,
    max_tokens=512
)
```

### 3. SQL Database Toolkit Setup
```python
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.prompt import SQL_PREFIX, SQL_FUNCTIONS_SUFFIX

# Create toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
```

### 4. Creating the SQL Chain
```python
from langchain.chains import create_sql_query_chain
from langchain.prompts import ChatPromptTemplate

# Create a chain for SQL query generation
chain = create_sql_query_chain(llm, db)

# Example usage
query = "What are the total number of projects in Malawi?"
sql_query = chain.invoke({"question": query})
```

### 5. Implementing the Question-Answering System
```python
from langchain_community.chains import SQLDatabaseChain

# Create the database chain
db_chain = SQLDatabaseChain.from_llm(
    llm=llm, 
    db=db, 
    verbose=True,
    return_intermediate_steps=True
)

# Example usage
response = db_chain.run(
    "How many projects are there in each district?"
)
```

## Best Practices

1. **Error Handling**:
   - Always validate SQL queries before execution
   - Implement proper error handling for database connections
   - Handle LLM API rate limits and errors

2. **Security**:
   - Never expose database credentials in code
   - Use environment variables for sensitive information
   - Implement proper SQL injection prevention

3. **Performance**:
   - Use connection pooling for database connections
   - Implement caching where appropriate
   - Monitor and optimize query performance

4. **Memory Management**:
   - Implement conversation memory for context
   - Clear memory when appropriate to prevent token limits
   - Use streaming for large responses

## Implementation Steps

1. Set up environment variables in `.env`:
   ```
   TOGETHER_API_KEY=your_api_key
   DATABASE_URL=your_database_url
   ```

2. Initialize the database connection and LLM in your main application

3. Create the necessary chains and tools

4. Implement the query processing logic

5. Add proper error handling and logging

6. Test the integration thoroughly

## Notes

- Always restart the FastAPI server after making changes to the integration
- Monitor token usage and database performance
- Regularly update dependencies to get the latest features and security fixes
- Implement proper logging for debugging and monitoring
