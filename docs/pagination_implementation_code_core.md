# Pagination Implementation - Core Components

This document provides the core code components needed to implement the pagination functionality.

## 1. Session Management

```python
# app/session.py
class SessionManager:
    """Manages query sessions for pagination and result caching"""
    
    def __init__(self, ttl: int = 3600):
        self.sessions = {}
        self.ttl = ttl
    
    def create_session(self, query: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "query": query,
            "original_query": query,
            "results": [],
            "total_results": 0,
            "current_page": 1,
            "page_size": 10,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "sql_query": ""
        }
        return session_id
    
    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            return None
        session = self.sessions[session_id]
        if time.time() - session["last_accessed"] > self.ttl:
            self.delete_session(session_id)
            return None
        session["last_accessed"] = time.time()
        return session
    
    def store_results(self, session_id: str, results, total_results: int, sql_query: str) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        self.sessions[session_id].update({
            "results": results,
            "total_results": total_results,
            "sql_query": sql_query
        })
        return True
    
    def get_page_results(self, session_id: str, page: int):
        session = self.get_session(session_id)
        if not session or not session["results"]:
            return None
            
        page_size = session["page_size"]
        total_results = session["total_results"]
        total_pages = (total_results + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            return None
            
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_results)
        
        if len(session["results"]) >= end_idx:
            page_results = session["results"][start_idx:end_idx]
        else:
            return None
            
        return {
            "results": page_results,
            "metadata": {
                "total_results": total_results,
                "current_page": page,
                "total_pages": total_pages,
                "page_size": page_size,
                "sql_query": session["sql_query"]
            },
            "pagination": {
                "has_more": page < total_pages,
                "has_previous": page > 1
            }
        }
```

## 2. Backend API Endpoint

```python
# app/main.py
@app.post("/api/rag-sql-chatbot/chat")
async def chat(request: Dict[str, Any]):
    message = request.get("message", "")
    session_id = request.get("session_id", None)
    
    # Check if this is a pagination request
    is_pagination = False
    page = 1
    
    pagination_commands = ["show more", "next page", "previous page", "page"]
    for cmd in pagination_commands:
        if cmd in message.lower():
            is_pagination = True
            break
    
    # Extract page number if specified
    if "page" in message.lower():
        import re
        page_match = re.search(r"page\s+(\d+)", message.lower())
        if page_match:
            try:
                page = int(page_match.group(1))
            except ValueError:
                pass
    
    # Handle pagination request
    if is_pagination and session_id:
        session = session_manager.get_session(session_id)
        if not session:
            return JSONResponse(content={
                "results": [{
                    "type": "error",
                    "message": "Your session has expired. Please try your original query again."
                }],
                "metadata": {"total_results": 0}
            })
        
        # Handle "next page" and "show more"
        if "next page" in message.lower() or "show more" in message.lower():
            page = session["current_page"] + 1
        
        # Handle "previous page"
        if "previous page" in message.lower():
            page = max(1, session["current_page"] - 1)
        
        # Get results for the requested page
        page_data = session_manager.get_page_results(session_id, page)
        if not page_data:
            # Need to fetch more data from database with offset
            # Use original query with pagination parameters
            # ...
            pass
        
        # Update current page in session
        session_manager.update_session(session_id, {"current_page": page})
        
        # Return the cached results directly
        return JSONResponse(content=page_data)
    
    # Handle regular query
    sql_integration = LangChainSQLIntegration()
    result = await sql_integration.process_query(message)
    
    # Create a new session for this query
    new_session_id = session_manager.create_session(message)
    
    # Extract and store results for potential pagination
    if "results" in result:
        total_results = result.get("metadata", {}).get("total_results", 0)
        sql_query = result.get("metadata", {}).get("sql_query", "")
        
        # Extract results data
        results_data = extract_results_data(result)
        
        session_manager.store_results(
            new_session_id, results_data, total_results, sql_query
        )
        
        # Add pagination metadata if needed
        if total_results > 10:
            if "pagination" not in result:
                result["pagination"] = {}
            
            result["pagination"]["session_id"] = new_session_id
            result["pagination"]["has_more"] = True
            result["pagination"]["next_page_command"] = "show more"
    
    return JSONResponse(content=result)
```

## 3. SQL Query Generation with Pagination

```python
# app/database/langchain_sql.py
async def process_paginated_query(self, user_query: str, limit: int = 10, offset: int = 0):
    """Process a query with pagination parameters"""
    start_time = time.time()
    
    try:
        # Generate the SQL query
        sql_query, query_type = await self.generate_sql_query(user_query)
        
        # Modify the query to include pagination
        if not sql_query.lower().strip().endswith(";"):
            sql_query += ";"
            
        # Remove existing LIMIT clause if present
        sql_query = re.sub(r"\s+LIMIT\s+\d+\s*;", ";", sql_query)
        
        # Add new LIMIT and OFFSET clauses
        sql_query = sql_query[:-1]  # Remove trailing semicolon
        sql_query += f" LIMIT {limit} OFFSET {offset};"
        
        # Execute the query
        results = await self.execute_query(sql_query)
        
        # Generate count query to get total results
        count_query = self.generate_count_query(sql_query)
        count_results = await self.execute_query(count_query)
        total_results = count_results[0].get("count", len(results))
        
        # Format the response
        response = await self.format_paginated_results(
            results, user_query, sql_query, query_type, total_results, limit, offset
        )
        
        return response
    except Exception as e:
        # Error handling
        return {
            "results": [{
                "type": "error",
                "message": f"Error processing paginated query: {str(e)}"
            }],
            "metadata": {
                "total_results": 0,
                "query_time": f"{time.time() - start_time:.2f}s",
                "sql_query": ""
            }
        }
```

## 4. Formatting Results - Direct vs. LLM Approach

```python
async def format_paginated_results(
    self, results, user_query: str, sql_query: str, query_type: str,
    total_results: int, limit: int, offset: int
):
    """Format paginated results with or without LLM assistance"""
    current_page = (offset // limit) + 1
    total_pages = (total_results + limit - 1) // limit
    start_index = offset + 1
    end_index = min(offset + limit, total_results)
    
    # For standard result types, format directly (token saving)
    if query_type in ["district_query", "sector_query", "status_query"]:
        formatted_results = []
        
        # Add header message
        if offset == 0:
            message = f"Found {total_results} results. Showing {start_index}-{end_index}:"
        else:
            message = f"Showing results {start_index}-{end_index} of {total_results}:"
            
        formatted_results.append({
            "type": "text",
            "message": message,
            "data": {}
        })
        
        # Format each result item
        for i, result in enumerate(results, 1):
            item_num = offset + i
            formatted_result = {
                "type": "text",
                "message": f"Result {item_num}:\n" + self.format_result_item(result, query_type),
                "data": {}
            }
            formatted_results.append(formatted_result)
            
        # Calculate pagination metadata
        pagination = {
            "has_more": current_page < total_pages,
            "has_previous": current_page > 1,
            "current_page": current_page,
            "total_pages": total_pages,
            "next_page_command": "show more" if current_page < total_pages else None,
            "prev_page_command": "previous page" if current_page > 1 else None
        }
        
        return {
            "results": formatted_results,
            "metadata": {
                "total_results": total_results,
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": limit,
                "query_time": f"{time.time() - self.start_time:.2f}s",
                "sql_query": sql_query
            },
            "pagination": pagination
        }
    
    # For complex queries or first page, use LLM to format results
    if offset == 0 or query_type not in ["district_query", "sector_query", "status_query"]:
        return await self.generate_natural_response(
            results, 
            user_query, 
            sql_query, 
            query_type,
            pagination_info={
                "total_results": total_results,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_more": current_page < total_pages
            }
        )
    
    # Fallback to direct formatting
    return self.format_direct_response(results, total_results, current_page, total_pages, limit, sql_query)
```

## 5. Frontend Chat Component (React)

```jsx
// Frontend pagination handling (simplified)
const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [paginationInfo, setPaginationInfo] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const payload = { message: userMessage };
      
      // Add session ID if this is a pagination request
      if (sessionId && isPaginationCommand(userMessage)) {
        payload.session_id = sessionId;
      }

      const response = await axios.post('/api/rag-sql-chatbot/chat', payload);
      const data = response.data;
      
      // Process bot response
      const botMessage = {
        type: 'bot',
        content: formatBotResponse(data.results),
        metadata: data.metadata || {},
        pagination: data.pagination || null
      };
      
      // Store session ID if provided
      if (data.pagination && data.pagination.session_id) {
        setSessionId(data.pagination.session_id);
      }
      
      // Store pagination info
      setPaginationInfo(data.pagination || null);
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, I encountered an error processing your request.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Add pagination buttons to UI
  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              {typeof msg.content === 'string' ? msg.content : msg.content}
              
              {/* Pagination controls */}
              {msg.type === 'bot' && msg.pagination && (
                <div className="pagination-controls">
                  {msg.pagination.has_previous && (
                    <button 
                      onClick={() => handlePaginationClick(msg.pagination.prev_page_command)}
                      className="pagination-button"
                    >
                      Previous
                    </button>
                  )}
                  
                  {msg.pagination.current_page && msg.pagination.total_pages && (
                    <span className="pagination-info">
                      Page {msg.pagination.current_page} of {msg.pagination.total_pages}
                    </span>
                  )}
                  
                  {msg.pagination.has_more && (
                    <button 
                      onClick={() => handlePaginationClick(msg.pagination.next_page_command)}
                      className="pagination-button"
                    >
                      Next
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Form for input */}
      <form onSubmit={handleSubmit}>
        {/* Input fields */}
      </form>
    </div>
  );
};
```

## Implementation Checklist

1. Create `SessionManager` class
2. Update backend API endpoint to detect pagination commands
3. Implement SQL query modification for pagination
4. Add direct result formatting functions to save tokens
5. Update LLM prompts to include pagination information
6. Add session storage and caching for results
7. Create frontend support for pagination commands and controls
8. Add database indexes for optimized performance
9. Implement testing for pagination functionality 