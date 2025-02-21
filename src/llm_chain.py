from dotenv import load_dotenv
import os
import time
from langchain_community.utilities import SQLDatabase
from langchain_together import Together
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.memory import BaseMemory
from langchain.memory import ConversationBufferMemory
from src.result_handler import ResultHandler, get_column_names, format_answer_section
from src.config import initialize_config, LangChainConfig
from src.rag_components import RAGComponents
from app.core.logger import logger
from app.core.langsmith_config import langsmith_config
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tracers.context import tracing_v2_enabled
from langchain.callbacks.manager import CallbackManager

# Load environment variables
load_dotenv()

class ProjectQueryChain(BaseModel):
    """Chain for processing project-related questions"""
    config: LangChainConfig = Field(default_factory=initialize_config)
    together: Together | None = Field(default=None)
    db: SQLDatabase | None = Field(default=None)
    memory: ConversationBufferMemory | None = Field(default=None)
    result_handler: ResultHandler | None = Field(default=None)
    rag: RAGComponents | None = Field(default=None)
    qa_chain: Any | None = Field(default=None)
    logger: Any = Field(default=logger)
    langsmith: Any = Field(default=langsmith_config)
    usage_stats: Dict[str, Any] = Field(default_factory=lambda: {
        'total_queries': 0,
        'total_tokens': 0,
        'total_api_calls': 0,
        'avg_response_time': 0.0,
        'error_count': 0
    })

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **data):
        super().__init__(**data)
        self.together = None

    async def initialize(self):
        """Initialize all components asynchronously"""
        try:
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                logger.error("TOGETHER_API_KEY environment variable not set")
                raise ValueError("TOGETHER_API_KEY environment variable not set")
            
            # Initialize Together client with API key and config
            llm_kwargs = self.config.get_llm_kwargs()
            
            # Initialize Together without callbacks
            self.together = Together(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
                together_api_key=api_key
            )
            
            # Test the API connection
            logger.info("Testing Together API connection...")
            start_time = time.time()
            
            # Test API connection
            response = await self.together.ainvoke("Test message")
            
            api_latency = time.time() - start_time
            
            if not response:
                logger.error("Failed to get response from Together API")
                raise ValueError("Failed to get response from Together API")
            
            logger.info(f"Together API connection successful (latency: {api_latency:.2f}s)")
            self.usage_stats['total_api_calls'] += 1
            
        except Exception as e:
            logger.error(f"Error initializing Together API: {str(e)}")
            self.usage_stats['error_count'] += 1
            raise
        
        # Initialize other components
        logger.info("Initializing database connection...")
        db_kwargs = self.config.get_db_kwargs()
        self.db = SQLDatabase.from_uri(
            "sqlite:///malawi_projects1.db",
            **db_kwargs
        )
        
        logger.info("Initializing memory components...")
        memory_kwargs = self.config.get_memory_kwargs()
        self.memory = ConversationBufferMemory(**memory_kwargs)
        
        logger.info("Initializing result handler...")
        self.result_handler = ResultHandler()
        
        logger.info("Initializing RAG components...")
        self.rag = RAGComponents(self.together, self.memory)
        
        logger.info("Initializing QA chain...")
        self.qa_chain = self.rag.create_qa_chain()
    
        logger.info("Initialization complete")
        return self

    @langsmith_config.trace_chain("sql_generation")
    async def _generate_sql_query(self, question: str) -> str:
        """Generate SQL query using Together AI and few-shot examples"""
        try:
            start_time = time.time()
            logger.info(f"Generating SQL query for question: {question}")
            
            # Get few-shot prompt from RAG components
            prompt = self.rag.few_shot_prompt.format(input=question)
            
            # Generate SQL query
            response = await self.together.ainvoke(prompt)
            
            query_gen_time = time.time() - start_time
            logger.info(f"SQL query generated in {query_gen_time:.2f}s")
            
            self.usage_stats['total_api_calls'] += 1
            self.usage_stats['avg_response_time'] = (
                (self.usage_stats['avg_response_time'] * self.usage_stats['total_queries'] + query_gen_time) /
                (self.usage_stats['total_queries'] + 1)
            )
            
            # Extract only the first SQL query from the response
            sql_lines = [line.strip() for line in response.split('\n') if line.strip()]
            for line in sql_lines:
                if line.upper().startswith('SELECT'):
                    # Find the end of the query (marked by semicolon)
                    query_end = line.find(';')
                    if query_end != -1:
                        sql_query = line[:query_end + 1]
                    else:
                        sql_query = line + ';'
                    logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
            logger.error("No valid SQL query found in response")
            raise ValueError("No valid SQL query found in response")
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            self.usage_stats['error_count'] += 1
            raise
    
    @langsmith_config.trace_chain("query_processing")
    async def invoke(self, question: str) -> Dict[str, Any]:
        """Process a question and return the answer with metadata"""
        start_time = time.time()
        
        # Validate input
        if not question or not question.strip():
            self.usage_stats['error_count'] += 1
            raise ValueError("Question cannot be empty")
            
        self.logger.info(f"Processing question: {question}")
        
        try:
            # Update usage statistics
            self.usage_stats['total_queries'] += 1
            
            # Generate and execute SQL query
            sql_query = await self._generate_sql_query(question)
            logger.info(f"Executing SQL query: {sql_query}")
            results = self.db.run(sql_query)
            
            # Process results through QA chain
            context = {
                "question": question,
                "sql_results": results
            }
            
            # Add tracing for QA chain
            logger.info("Generating answer using QA chain")
            answer = await self.qa_chain.ainvoke(context)
            
            # Generate follow-up suggestions
            context["current_answer"] = answer
            logger.info("Generating follow-up suggestions")
            suggestions = await self.rag.generate_suggestions(context)
            
            # Update memory
            self.memory.save_context(
                {"input": question},
                {"output": answer}
            )
            
            total_time = time.time() - start_time
            logger.info(f"Question processed in {total_time:.2f}s")
            
            # Update response time statistics
            self.usage_stats['avg_response_time'] = (
                (self.usage_stats['avg_response_time'] * (self.usage_stats['total_queries'] - 1) + total_time) /
                self.usage_stats['total_queries']
            )
            
            return {
                "answer": answer,
                "sql_query": sql_query,
                "results": results,
                "suggestions": suggestions,
                "processing_time": total_time,
                "usage_stats": self.usage_stats
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            self.usage_stats['error_count'] += 1
            raise

async def initialize_chain():
    """Initialize and return a ProjectQueryChain instance."""
    chain = ProjectQueryChain()
    return await chain.initialize() 