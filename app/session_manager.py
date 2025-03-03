from typing import Dict, Any, List, Optional
import time
import uuid

class SessionManager:
    """Manages query sessions for pagination and result caching"""
    
    def __init__(self, ttl: int = 3600):
        """Initialize session manager with time-to-live in seconds"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
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