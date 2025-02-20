# LLM Integration with LangChain

## 1. Setup & Configuration
- [x] Install LangChain and dependencies
  ```bash
  pip install langchain langchain-community python-dotenv together
  ```
- [x] Set up environment variables in .env
  ```bash
  TOGETHER_API_KEY=your_api_key
  ```
- [x] Choose LLM provider (Together AI - meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K)
- [ ] Configure LangChain settings

## 2. Core Integration
- [x] Set up LangChain components
  - [x] Initialize LLM (using LangChain's LLM wrapper)
  - [x] Set up SQLDatabase connection
  - [x] Configure conversation memory
- [ ] Create chains
  - [ ] SQL Chain for database queries
  - [ ] Conversation Chain for chat history
  - [ ] Question-answering Chain for RAG

## 3. Query Processing
- [x] Implement SQL Database Chain
  - [x] Configure SQLDatabaseChain
  - [ ] Set up few-shot examples
  - [x] Add custom prompts
- [x] Add query validation
  - [x] Use custom validators
  - [x] Add error handling
- [x] Handle edge cases
  - [x] Implement error handling
  - [x] Add fallback responses

## 4. Response Generation
- [x] Set up output parsers
  - [x] SQL results formatter
  - [x] Natural language generator
- [x] Create response templates
  - [x] Specific project template
  - [x] General query template
  - [x] Error message template
- [ ] Implement follow-ups
  - [ ] Add suggestion chain
  - [x] Configure memory for context

## 5. Testing
- [x] Unit tests
  - [x] Test LLM integration
  - [x] Test query parsing
  - [ ] Test chain components
  - [x] Test output parsers
- [ ] Integration tests
  - [x] Test conversation flow
  - [ ] Test chain combinations
  - [ ] Test memory persistence
- [x] Performance testing
  - [x] Measure chain execution times
  - [x] Test concurrent requests
  - [x] Monitor token usage

## 6. Monitoring & Maintenance
- [x] Set up logging
  - [x] Chain execution logs
  - [x] Error tracking
  - [x] Usage statistics
- [ ] Set up LangSmith (optional)
  - [ ] Configure tracing
  - [ ] Set up debugging
  - [ ] Monitor chain performance

## Quick Reference

### Key LangChain Components:
1. `SQLDatabase` - Database connection
2. `ConversationBufferMemory` - Chat history
3. `PromptTemplate` - Custom prompts
4. `OutputParser` - Response formatting

### Example Code Snippets:

```python
# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Database setup
from langchain_community.utilities import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///malawi_projects1.db")

# LLM setup with Together AI
from langchain_community.llms import Together
llm = Together(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
    together_api_key=os.getenv("TOGETHER_API_KEY"),
    temperature=0.7,
    max_tokens=512
)

# Create conversation memory
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create chat prompt
from langchain.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant for querying Malawi infrastructure projects."),
    ("human", "{question}")
])
```

### Important Files:
1. `chains.py` - LangChain setup
2. `prompts.py` - Custom prompts
3. `parsers.py` - Output parsers
4. `memory.py` - Conversation memory

### Testing:
```bash
# Test chains
pytest tests/test_chains.py

# Test prompts
pytest tests/test_prompts.py

# Run integration tests
pytest tests/integration/
``` 