# Pagination Implementation Code Examples

This document provides code examples to implement the pagination functionality outlined in the pagination implementation plan.

## Backend Implementation

### 1. Session State Management

```python
# app/session.py

from typing import Dict, Any, List, Optional
import time
import uuid

class SessionManager:
    """Manages query sessions for pagination and result caching"""
    
    def __init__(self, ttl: int = 3600):
        """Initialize session manager with time-to-live in seconds"""
        self.sessions = {}
        self.ttl = ttl  # Time to live in seconds
    
    def create_session(self, query: str) -> str:
        """Create a new session for a query"""
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
            "sql_query": "",
            "is_paginated": False
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data for a session ID"""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        # Check if session has expired
        if time.time() - session["last_accessed"] > self.ttl:
            self.delete_session(session_id)
            return None
            
        # Update last accessed time
        session["last_accessed"] = time.time()
        return session
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if not session:
            return False
            
        self.sessions[session_id].update(data)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def store_results(self, session_id: str, results: List[Dict[str, Any]], 
                      total_results: int, sql_query: str) -> bool:
        """Store query results in the session"""
        session = self.get_session(session_id)
        if not session:
            return False
            
        self.sessions[session_id].update({
            "results": results,
            "total_results": total_results,
            "sql_query": sql_query,
            "is_paginated": total_results > session["page_size"]
        })
        return True
    
    def get_page_results(self, session_id: str, page: int) -> Optional[Dict[str, Any]]:
        """Get results for a specific page"""
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
        
        # Calculate actual results based on stored data
        if len(session["results"]) >= end_idx:
            # We have the full cached results
            page_results = session["results"][start_idx:end_idx]
        else:
            # We need to fetch more results
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
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session["last_accessed"] > self.ttl
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
```

### 2. API Endpoint Modifications

```python
# app/main.py (or your FastAPI app file)

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from .session import SessionManager
from .database.langchain_sql import LangChainSQLIntegration

app = FastAPI()
session_manager = SessionManager()

@app.post("/api/rag-sql-chatbot/chat")
async def chat(request: Dict[str, Any], req: Request):
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
                    "message": "Your session has expired. Please try your original query again.",
                    "data": {}
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
            # Need to fetch more data
            sql_integration = LangChainSQLIntegration()
            original_query = session["original_query"]
            page_size = session["page_size"]
            offset = (page - 1) * page_size
            
            # Generate paginated SQL query
            paginated_results = await sql_integration.process_paginated_query(
                original_query, page_size, offset
            )
            
            # Format the response based on the type of data
            # This could be directly formatted or sent to LLM for formatting
            return JSONResponse(content=paginated_results)
        
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
        
        # Get actual results data
        results_data = []
        for item in result["results"]:
            if item.get("type") == "list" and "data" in item:
                if "values" in item["data"]:
                    results_data.extend(item["data"]["values"])
        
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

### 3. SQL Query Generation with Pagination

```python
# app/database/langchain_sql.py

async def process_paginated_query(self, user_query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
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
        logger.info(f"Executing paginated SQL query: {sql_query}")
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
        logger.error(f"Error processing paginated query: {str(e)}")
        return {
            "results": [{
                "type": "error",
                "message": f"Error processing paginated query: {str(e)}",
                "data": {}
            }],
            "metadata": {
                "total_results": 0,
                "query_time": f"{time.time() - start_time:.2f}s",
                "sql_query": ""
            }
        }

def generate_count_query(self, sql_query: str) -> str:
    """Generate a count query from a SELECT query"""
    # Parse the original query
    from_pos = sql_query.lower().find("from")
    where_pos = sql_query.lower().find("where")
    
    if from_pos == -1:
        return "SELECT COUNT(*) as count FROM proj_dashboard;"
    
    # Extract FROM clause and beyond
    if where_pos != -1:
        from_clause = sql_query[from_pos:where_pos]
        where_clause = sql_query[where_pos:]
        
        # Remove ORDER BY, LIMIT and OFFSET clauses
        order_pos = where_clause.lower().find("order by")
        limit_pos = where_clause.lower().find("limit")
        
        if order_pos != -1:
            where_clause = where_clause[:order_pos]
        elif limit_pos != -1:
            where_clause = where_clause[:limit_pos]
        
        return f"SELECT COUNT(*) as count {from_clause} {where_clause};"
    
    # No WHERE clause
    remaining = sql_query[from_pos:]
    order_pos = remaining.lower().find("order by")
    limit_pos = remaining.lower().find("limit")
    
    if order_pos != -1:
        remaining = remaining[:order_pos]
    elif limit_pos != -1:
        remaining = remaining[:limit_pos]
    
    return f"SELECT COUNT(*) as count {remaining};"

async def format_paginated_results(
    self, results: List[Dict[str, Any]], 
    user_query: str, 
    sql_query: str, 
    query_type: str,
    total_results: int,
    limit: int,
    offset: int
) -> Dict[str, Any]:
    """Format paginated results with or without LLM assistance"""
    current_page = (offset // limit) + 1
    total_pages = (total_results + limit - 1) // limit
    start_index = offset + 1
    end_index = min(offset + limit, total_results)
    
    # For standard result types, format directly
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
    return self.format_direct_response(
        results, 
        total_results,
        current_page,
        total_pages,
        limit,
        sql_query
    )

def format_result_item(self, result: Dict[str, Any], query_type: str) -> str:
    """Format a single result item based on query type"""
    if query_type == "district_query":
        parts = []
        if "project_name" in result:
            parts.append(f"Name of project: {result.get('project_name', 'Unknown')}")
        if "fiscal_year" in result:
            parts.append(f"Fiscal year: {result.get('fiscal_year', 'Unknown')}")
        if "location" in result:
            parts.append(f"Location: {result.get('location', 'Unknown')}")
        if "total_budget" in result:
            budget = result.get('total_budget', 0)
            parts.append(f"Budget: MWK {float(budget):,.2f}" if budget else "Budget: Unknown")
        if "status" in result:
            parts.append(f"Status: {result.get('status', 'Unknown')}")
        if "project_sector" in result:
            parts.append(f"Project Sector: {result.get('project_sector', 'Unknown')}")
        
        return "\n".join(parts)
    
    elif query_type == "sector_query":
        # Similar formatting for sector queries
        pass
    
    # Default formatting for other query types
    return "\n".join([f"{k}: {v}" for k, v in result.items()])
```

## Frontend Implementation

### 1. Chat Component with Pagination

```javascript
// frontend/components/Chat.js

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [paginationInfo, setPaginationInfo] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const payload = {
        message: userMessage
      };
      
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

  const isPaginationCommand = (text) => {
    const paginationCommands = ['show more', 'next page', 'previous page', 'page'];
    return paginationCommands.some(cmd => text.toLowerCase().includes(cmd));
  };

  const formatBotResponse = (results) => {
    if (!results || !Array.isArray(results)) {
      return 'No results found.';
    }
    
    return results.map((item, index) => {
      if (item.type === 'text') {
        return <p key={index}>{item.message}</p>;
      } else if (item.type === 'list' && item.data) {
        return (
          <div key={index}>
            <h4>{item.message}</h4>
            <table className="results-table">
              <thead>
                <tr>
                  {item.data.fields.map((field, i) => (
                    <th key={i}>{field}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {item.data.values.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {item.data.fields.map((field, cellIndex) => (
                      <td key={cellIndex}>{row[field]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      } else {
        return <p key={index}>Unsupported message type</p>;
      }
    });
  };

  const handlePaginationClick = (command) => {
    if (!command) return;
    setInput(command);
    handleSubmit({ preventDefault: () => {} });
  };

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
              
              {/* Metadata display (optional) */}
              {msg.type === 'bot' && msg.metadata && msg.metadata.query_time && (
                <div className="message-metadata">
                  Query time: {msg.metadata.query_time}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="message-content loading">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Pagination quick actions */}
      {paginationInfo && (
        <div className="pagination-quick-actions">
          {paginationInfo.has_previous && (
            <button onClick={() => handlePaginationClick('previous page')}>
              ← Previous Page
            </button>
          )}
          
          {paginationInfo.has_more && (
            <button onClick={() => handlePaginationClick('show more')}>
              Show More →
            </button>
          )}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
```

### 2. CSS Styling for Pagination

```css
/* frontend/styles/chat.css */

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 10px;
  line-height: 1.5;
}

.message.user {
  align-self: flex-end;
  background-color: #dcf8c6;
}

.message.bot {
  align-self: flex-start;
  background-color: #f1f1f1;
}

.pagination-controls {
  display: flex;
  align-items: center;
  margin-top: 10px;
  gap: 10px;
}

.pagination-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.pagination-button:hover {
  background-color: #3e8e41;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-quick-actions {
  display: flex;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: #f9f9f9;
  border-top: 1px solid #ddd;
}

.pagination-quick-actions button {
  background-color: transparent;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 15px;
  cursor: pointer;
  color: #555;
}

.pagination-quick-actions button:hover {
  background-color: #f1f1f1;
}

.message-metadata {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.loading .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  margin-right: 5px;
  animation: dot-pulse 1.4s infinite ease-in-out;
}

.loading .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-container {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
}

.input-container input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  margin-right: 10px;
}

.input-container button {
  padding: 10px 20px;
  background-color: #128C7E;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.input-container button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.results-table th, .results-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.results-table th {
  background-color: #f2f2f2;
}

.results-table tr:nth-child(even) {
  background-color: #f9f9f9;
}
```

## Database Optimization

To optimize database queries for pagination, add indexes to commonly searched fields:

```sql
-- Add indexes to improve pagination performance
CREATE INDEX IF NOT EXISTS idx_district ON proj_dashboard (district);
CREATE INDEX IF NOT EXISTS idx_projectsector ON proj_dashboard (projectsector);
CREATE INDEX IF NOT EXISTS idx_projectstatus ON proj_dashboard (projectstatus);
CREATE INDEX IF NOT EXISTS idx_fiscalyear ON proj_dashboard (fiscalyear);
CREATE INDEX IF NOT EXISTS idx_budget ON proj_dashboard (budget);
```

## Testing

Here's a simple test script for the pagination functionality:

```python
# tests/test_pagination.py

import unittest
import asyncio
from app.session import SessionManager
from app.database.langchain_sql import LangChainSQLIntegration

class TestPagination(unittest.TestCase):
    def setUp(self):
        self.session_manager = SessionManager(ttl=60)  # Short TTL for testing
        self.sql_integration = LangChainSQLIntegration()
    
    def test_session_management(self):
        # Create a session
        session_id = self.session_manager.create_session("Test query")
        self.assertIsNotNone(session_id)
        
        # Get session
        session = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session["query"], "Test query")
        
        # Update session
        self.session_manager.update_session(session_id, {"current_page": 2})
        session = self.session_manager.get_session(session_id)
        self.assertEqual(session["current_page"], 2)
        
        # Store results
        results = [{"name": "Test1"}, {"name": "Test2"}]
        self.session_manager.store_results(session_id, results, 2, "SELECT * FROM test")
        session = self.session_manager.get_session(session_id)
        self.assertEqual(len(session["results"]), 2)
        
        # Get page results
        page_data = self.session_manager.get_page_results(session_id, 1)
        self.assertIsNotNone(page_data)
        self.assertEqual(len(page_data["results"]), 2)
        
        # Delete session
        self.session_manager.delete_session(session_id)
        session = self.session_manager.get_session(session_id)
        self.assertIsNone(session)
    
    def test_session_expiry(self):
        # Create a session with a very short TTL
        self.session_manager.ttl = 0.1  # 100ms
        session_id = self.session_manager.create_session("Expiring query")
        
        # Wait for session to expire
        import time
        time.sleep(0.2)
        
        # Try to get the expired session
        session = self.session_manager.get_session(session_id)
        self.assertIsNone(session)
    
    def test_generate_count_query(self):
        # Test various SQL query transformations
        test_cases = [
            (
                "SELECT * FROM proj_dashboard WHERE district = 'Zomba' LIMIT 10;",
                "SELECT COUNT(*) as count FROM proj_dashboard WHERE district = 'Zomba';"
            ),
            (
                "SELECT name FROM proj_dashboard WHERE budget > 1000 ORDER BY name LIMIT 5 OFFSET 10;",
                "SELECT COUNT(*) as count FROM proj_dashboard WHERE budget > 1000;"
            ),
            (
                "SELECT * FROM proj_dashboard;",
                "SELECT COUNT(*) as count FROM proj_dashboard;"
            )
        ]
        
        for input_query, expected_output in test_cases:
            count_query = self.sql_integration.generate_count_query(input_query)
            self.assertEqual(count_query, expected_output)
    
    def test_paginated_query(self):
        # This test requires running against a real database
        async def run_test():
            result = await self.sql_integration.process_paginated_query(
                "Show projects in Zomba district", 5, 0
            )
            self.assertIn("results", result)
            self.assertIn("metadata", result)
            self.assertIn("pagination", result)
            
            # Check pagination metadata
            metadata = result["metadata"]
            self.assertIn("total_results", metadata)
            self.assertIn("current_page", metadata)
            self.assertEqual(metadata["current_page"], 1)
            
            # Check that results are limited to 5
            results_count = 0
            for item in result["results"]:
                if item.get("type") == "text" and "Project" in item.get("message", ""):
                    results_count += 1
            
            self.assertLessEqual(results_count, 5)
        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
```

## Deployment Checklist

- [ ] Update database schema with necessary indexes
- [ ] Deploy new backend code with pagination functionality
- [ ] Update frontend to handle pagination controls
- [ ] Test pagination with large result sets
- [ ] Monitor token usage with and without LLM assistance
- [ ] Update documentation with examples for pagination commands 