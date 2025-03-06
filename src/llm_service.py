"""
LLM Service using Together AI for RAG SQL Chatbot
"""

import os
import logging
from typing import Dict, List, Optional
from langchain.llms import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Handler for LLM operations using Together AI"""
    
    def __init__(self):
        """Initialize LLM Handler with Together AI API"""
        self.api_key = os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
        logger.info(f"Together API Key found: {self.api_key[:4]}...{self.api_key[-4:]}")
        
        # Get LLM configuration from environment
        self.model = os.getenv("LLM_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1500"))
        self.top_k = int(os.getenv("LLM_TOP_K", "50"))
        self.top_p = float(os.getenv("LLM_TOP_P", "0.7"))
        self.repetition_penalty = float(os.getenv("LLM_REPETITION_PENALTY", "1.1"))
        
        # Initialize Together LLM
        self.llm = Together(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_k=self.top_k,
            top_p=self.top_p,
            repetition_penalty=self.repetition_penalty
        )
        logger.info(f"Successfully initialized Together API with model {self.model}")
    
    def get_system_prompt(self, language: str) -> str:
        """Generate system prompt based on language"""
        prompts = {
            "russian": "Вы - ассистент по инфраструктурным проектам в Малави. Предоставьте четкий и структурированный ответ на русском языке.",
            "uzbek": "Siz Malavining infratuzilma loyihalari bo'yicha yordamchisiz. O'zbek tilida aniq va tuzilgan javob bering.",
            "english": "You are an infrastructure projects assistant for Malawi. Provide clear and structured responses in English."
        }
        return prompts.get(language.lower(), prompts["english"])
    
    def format_chat_context(self, chat_history: List[Dict]) -> str:
        """Format chat history for context"""
        try:
            context_messages = []
            for msg in chat_history[-5:]:  # Get last 5 messages
                role = "User" if msg.get("type") == "query" else "Assistant"
                text = msg.get("text", "")
                if text:
                    context_messages.append(f"{role}: {text}")
            return "\n".join(context_messages)
        except Exception as e:
            logger.error(f"Error formatting chat context: {str(e)}")
            return ""  # Return empty context on error
    
    def enhance_query(self, query: str) -> str:
        """Enhance the user query for better results"""
        try:
            prompt = f"""Given this user query about Malawi infrastructure projects:
"{query}"

Please enhance this query to be more specific and detailed while maintaining its original intent.
Focus on infrastructure projects, locations, budgets, and timelines.

Enhanced query:"""
            
            response = self.llm.invoke(prompt)
            enhanced_query = response.strip().split("\n")[0]  # Take first line
            logger.info(f"Enhanced query: {enhanced_query}")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error enhancing query: {str(e)}")
            return query  # Return original query if enhancement fails
    
    def generate_suggestions(self, response: str, language: str) -> List[str]:
        """Generate follow-up questions based on the response"""
        try:
            prompt_templates = {
                "english": """Based on this response about Malawi infrastructure projects:
"{response}"

Generate 3 relevant follow-up questions that would help explore more details about the projects mentioned.
Format: Just the questions, one per line, no numbering.""",
                
                "russian": """На основе этого ответа о инфраструктурных проектах в Малави:
"{response}"

Создайте 3 релевантных последующих вопроса, которые помогут узнать больше деталей об упомянутых проектах.
Формат: Только вопросы, по одному в строке, без нумерации.""",
                
                "uzbek": """Malavining infratuzilma loyihalari haqidagi ushbu javobga asoslanib:
"{response}"

Loyihalar haqida ko'proq ma'lumot olishga yordam beradigan 3 ta tegishli savol tuzing.
Format: Faqat savollar, har bir satr uchun bitta, raqamlarsiz."""
            }
            
            prompt = prompt_templates.get(language.lower(), prompt_templates["english"])
            prompt = prompt.format(response=response)
            
            response = self.llm.invoke(prompt)
            suggestions = [q.strip() for q in response.strip().split("\n") if q.strip()]
            return suggestions[:4]  # Return up to 4 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []  # Return empty list if generation fails
    
    def process_query(
        self,
        query: str,
        chat_history: List[Dict],
        language: str = "english",
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Process a query using the LLM
        
        Args:
            query: User's query
            chat_history: List of previous chat messages
            language: Target language for response
            session_id: Optional session identifier
            
        Returns:
            Dict containing response and metadata
        """
        try:
            if not query.strip():
                return {
                    "error": "Empty query",
                    "llm_processing": {
                        "model": self.model,
                        "response_formatted": False,
                        "enhanced_query": query,
                        "suggested_questions": []
                    },
                    "session_id": session_id
                }
            
            # Prepare system prompt and context
            system_prompt = self.get_system_prompt(language)
            context = self.format_chat_context(chat_history)
            
            # Enhance the query
            enhanced_query = self.enhance_query(query)
            
            # Build the full prompt
            prompt = f"""{system_prompt}

Previous conversation:
{context}

Current query: {enhanced_query}

Please provide a response in the following format:
1. Project: Name and brief description of the project(s)
2. Location: Specific location details (region, district, city)

Important: 
- Your response MUST be in {language} language
- Only include Project and Location information
- Keep responses concise and focused
- Do not include other categories like budget, status, or statistics

Response:"""
            
            # Generate response
            response = self.llm.invoke(prompt)
            response_text = response.strip()
            
            # Generate follow-up suggestions
            suggested_questions = self.generate_suggestions(response_text, language)
            
            return {
                "response": response_text,
                "llm_processing": {
                    "model": self.model,
                    "response_formatted": True,
                    "enhanced_query": enhanced_query,
                    "suggested_questions": suggested_questions
                },
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Return a more graceful error response
            return {
                "error": f"Error processing query: {str(e)}",
                "response": "I apologize, but I encountered an error processing your query. Please try again.",
                "llm_processing": {
                    "model": self.model,
                    "response_formatted": False,
                    "enhanced_query": query,
                    "suggested_questions": []
                },
                "session_id": session_id
            }

    def classify_query(self, query: str, chat_history: List[Dict] = None) -> Dict:
        """
        Classify the query type and extract key information using LLM
        
        Args:
            query: User's query
            chat_history: Optional list of previous chat messages for context
            
        Returns:
            Dict containing query classification and extracted information
        """
        try:
            # Format chat history for context
            context = ""
            if chat_history:
                context = "Previous conversation:\n"
                for msg in chat_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg.get("type") == "query" else "Assistant"
                    text = msg.get("text", "")
                    if text:
                        context += f"{role}: {text}\n"
            
            prompt = f"""Analyze this query about Malawi infrastructure projects and classify it:
"{query}"

{context}

Please classify the query and extract key information in the following JSON format:
{{
    "query_type": "unrelated" | "general" | "specific",
    "context": {{
        "previous_project": "string or null",  // Name of project from previous messages
        "conversation_topic": "string",         // Current topic being discussed
        "extracted_filters": {{                 // Any filters mentioned in the query
            "district": "string or null",
            "sector": "string or null",
            "status": "string or null",
            "budget": "string or null",
            "date": "string or null"
        }}
    }},
    "confidence": float between 0 and 1,
    "requires_db_query": boolean
}}

Guidelines:
1. Query Types:
   - unrelated: General conversation, greetings, or questions about system capabilities
   - general: Questions about multiple projects or general project information
   - specific: Questions about a specific project or follow-up questions about a project

2. Context Rules:
   - previous_project: Extract from chat history if available
   - conversation_topic: Current subject being discussed
   - extracted_filters: Any filters mentioned in the query

3. Examples:
   - unrelated: "hello", "what can you do?", "how are you?"
   - general: "show me projects in Lilongwe", "list all health projects"
   - specific: "tell me about the Water Project", "what's its budget?"

4. Confidence Scoring:
   - 1.0: Clear, unambiguous query
   - 0.7-0.9: Query with some ambiguity
   - 0.5-0.6: Unclear query requiring fallback
   - <0.5: Likely unrelated or invalid query

Response:"""
            
            response = self.llm.invoke(prompt)
            try:
                # Parse the JSON response
                import json
                classification = json.loads(response.strip())
                
                # Validate and clean the classification
                if not isinstance(classification, dict):
                    raise ValueError("Invalid classification format")
                
                # Ensure required fields exist
                required_fields = ["query_type", "context", "confidence", "requires_db_query"]
                for field in required_fields:
                    if field not in classification:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate query_type
                valid_types = ["unrelated", "general", "specific"]
                if classification["query_type"] not in valid_types:
                    raise ValueError(f"Invalid query_type: {classification['query_type']}")
                
                # Validate confidence
                if not 0 <= classification["confidence"] <= 1:
                    raise ValueError("Confidence must be between 0 and 1")
                
                # Log the classification
                logger.info(f"Query classification: {json.dumps(classification, indent=2)}")
                
                return classification
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM classification response: {str(e)}")
                return self._get_default_classification()
                
        except Exception as e:
            logger.error(f"Error classifying query: {str(e)}")
            return self._get_default_classification()
    
    def _get_default_classification(self) -> Dict:
        """Return a default classification for error cases"""
        return {
            "query_type": "general",
            "context": {
                "previous_project": None,
                "conversation_topic": "general",
                "extracted_filters": {
                    "district": None,
                    "sector": None,
                    "status": None,
                    "budget": None,
                    "date": None
                }
            },
            "confidence": 0.5,
            "requires_db_query": True
        }