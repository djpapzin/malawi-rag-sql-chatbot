"""
Conversation Store Module

This module handles the storage and retrieval of conversation logs.
"""

import json
import logging
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationStore:
    """
    Handles the storage and retrieval of conversation logs.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the conversation store.
        
        Args:
            storage_dir: Directory to store conversation logs. Defaults to app/logs.
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        # Create logs directory if it doesn't exist
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
    
    def get_recent_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent conversations from the logs.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation log entries
        """
        try:
            # Calculate the date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get all log files in the date range
            log_files = []
            for day in range(days):
                date = (end_date - timedelta(days=day)).strftime("%Y-%m-%d")
                log_file = os.path.join(self.storage_dir, f"responses_{date}.jsonl")
                if os.path.exists(log_file):
                    log_files.append(log_file)
            
            # Read all log entries
            conversations = []
            for log_file in log_files:
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            conversations.append(entry)
                        except json.JSONDecodeError:
                            logger.error(f"Error parsing log entry: {line}")
            
            # Sort by timestamp
            conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return conversations
        except Exception as e:
            logger.error(f"Error getting recent conversations: {str(e)}")
            return []
    
    def get_conversation_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a specific session.
        
        Args:
            session_id: Session ID to filter by
            
        Returns:
            List of conversation log entries for the session
        """
        try:
            # Get all log files
            log_files = glob.glob(os.path.join(self.storage_dir, "responses_*.jsonl"))
            
            # Read all log entries for the session
            conversations = []
            for log_file in log_files:
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("session_id") == session_id:
                                conversations.append(entry)
                        except json.JSONDecodeError:
                            logger.error(f"Error parsing log entry: {line}")
            
            # Sort by timestamp
            conversations.sort(key=lambda x: x.get("timestamp", ""))
            
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversation by session: {str(e)}")
            return []
    
    def clean_old_logs(self, days_to_keep: int = 30) -> int:
        """
        Clean up old log files.
        
        Args:
            days_to_keep: Number of days of logs to keep
            
        Returns:
            Number of files deleted
        """
        try:
            # Calculate the cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Get all log files
            log_files = glob.glob(os.path.join(self.storage_dir, "responses_*.jsonl"))
            
            # Delete old log files
            deleted_count = 0
            for log_file in log_files:
                try:
                    # Extract date from filename
                    filename = os.path.basename(log_file)
                    date_str = filename.replace("responses_", "").replace(".jsonl", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Check if file is older than cutoff date
                    if file_date < cutoff_date:
                        os.remove(log_file)
                        deleted_count += 1
                        logger.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    logger.error(f"Error processing log file {log_file}: {str(e)}")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning old logs: {str(e)}")
            return 0
