from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.memory import BaseMemory
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_together import Together
from pydantic import BaseModel, Field
from app.core.langsmith_config import langsmith_config
from langchain_core.tracers.context import tracing_v2_enabled
from langchain.callbacks.manager import CallbackManager

class RAGComponents(BaseModel):
    """Components for RAG-based question answering"""
    class Config:
        arbitrary_types_allowed = True

    llm: Together = Field(description="The language model to use")
    memory: ConversationBufferMemory = Field(description="Memory component for conversation history")
    few_shot_prompt: PromptTemplate = None
    qa_prompt: ChatPromptTemplate = None
    suggestions_prompt: ChatPromptTemplate = None

    def __init__(self, llm: Together, memory: ConversationBufferMemory):
        """Initialize RAG components"""
        # Get callback manager
        callback_manager = langsmith_config.get_callback_manager()
        
        # Update LLM with callbacks
        llm.callbacks = callback_manager
        
        super().__init__(llm=llm, memory=memory)
        self.few_shot_prompt = self._create_few_shot_prompt()
        self.qa_prompt = self._create_qa_prompt()
        self.suggestions_prompt = self._create_suggestions_prompt()

    def _create_few_shot_prompt(self) -> PromptTemplate:
        """Create few-shot prompt for SQL query generation"""
        template = """You are a helpful SQL assistant for a Malawi infrastructure project database. Given a question about projects, generate a SQL query to answer it.
        Use the following examples as a guide:

        Question: What is the total budget for all projects?
        SQL: SELECT SUM(budget) as total_budget FROM projects;

        Question: How many projects are there in each district?
        SQL: SELECT district, COUNT(*) as project_count FROM projects GROUP BY district ORDER BY project_count DESC;

        Question: What are the top 5 projects by budget?
        SQL: SELECT project_name, budget FROM projects ORDER BY budget DESC LIMIT 5;

        Question: Which projects are in Dowa?
        SQL: SELECT DISTINCT projectname, fiscalyear, district, budget, projectstatus, projectsector FROM proj_dashboard WHERE LOWER(district) LIKE '%dowa%' ORDER BY budget DESC;

        Question: Show me all projects in Zomba district
        SQL: SELECT DISTINCT projectname, fiscalyear, district, budget, projectstatus, projectsector FROM proj_dashboard WHERE LOWER(district) LIKE '%zomba%' ORDER BY budget DESC;

        Question: List projects in Lilongwe
        SQL: SELECT DISTINCT projectname, fiscalyear, district, budget, projectstatus, projectsector FROM proj_dashboard WHERE LOWER(district) LIKE '%lilongwe%' ORDER BY budget DESC;

        Now, please generate a SQL query for this question: {input}
        SQL: """
        return PromptTemplate.from_template(template)

    def _create_qa_prompt(self) -> ChatPromptTemplate:
        """Create prompt for question answering"""
        template = """Based on the SQL query results, please provide a clear and concise answer to the question.
        
        Question: {question}
        SQL Results: {sql_results}
        
        Please format your response in a clear and professional manner, using bullet points or paragraphs as appropriate.
        Include relevant numbers and statistics from the results.
        
        Answer: """
        return ChatPromptTemplate.from_template(template)

    def _create_suggestions_prompt(self) -> ChatPromptTemplate:
        """Create prompt for generating follow-up suggestions"""
        template = """Based on the current question and answer, suggest 3 relevant follow-up questions that the user might be interested in.
        
        Current Question: {question}
        Current Answer: {current_answer}
        
        Suggestions:
        1.
        2.
        3."""
        return ChatPromptTemplate.from_template(template)

    @langsmith_config.trace_chain("qa_chain")
    def create_qa_chain(self):
        """Create the question-answering chain"""
        # Create the chain with config handling
        chain = (
            {"question": RunnablePassthrough(), "sql_results": RunnablePassthrough()}
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    @langsmith_config.trace_chain("suggestions")
    async def generate_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate follow-up suggestions based on the current context"""
        # Format the prompt
        prompt = self.suggestions_prompt.format(**context)
        
        # Generate suggestions
        with tracing_v2_enabled(project_name="rag-sql-chatbot"):
            response = await self.llm.ainvoke(
                prompt,
                temperature=0.7,  # Higher temperature for more creative suggestions
                max_tokens=256
            )
        
        # Parse suggestions
        suggestions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and line[0].isdigit() and line[1] == '.':
                suggestions.append(line[2:].strip())
        
        return suggestions

    async def generate_answer(self, context: Dict[str, Any]) -> str:
        """Generate an answer based on the context"""
        # Format the prompt
        prompt = self.qa_prompt.format(**context)
        
        # Generate answer
        with tracing_v2_enabled(project_name="rag-sql-chatbot"):
            response = await self.llm.ainvoke(
                prompt,
                temperature=0.1,  # Lower temperature for more focused answers
                max_tokens=512
            )
        
        return response 