import pytest
from unittest.mock import Mock, patch
from src.rag_components import RAGComponents
from langchain.memory import ConversationBufferMemory

@pytest.fixture
def mock_together():
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="SELECT * FROM proj_dashboard"))]
    )
    return mock

@pytest.fixture
def mock_memory():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    return memory

def test_rag_initialization(mock_together, mock_memory):
    rag = RAGComponents(mock_together, mock_memory)
    assert rag.llm == mock_together
    assert rag.memory == mock_memory
    assert len(rag.examples) == 3
    assert rag.few_shot_prompt is not None

def test_few_shot_prompt(mock_together, mock_memory):
    rag = RAGComponents(mock_together, mock_memory)
    formatted_prompt = rag.few_shot_prompt.format(input="Show all projects in Zomba")
    assert "Show all projects in Zomba" in formatted_prompt
    assert "Given a question about Malawi infrastructure projects" in formatted_prompt
    assert "Let me analyze this question carefully" in formatted_prompt

def test_generate_suggestions(mock_together, mock_memory):
    mock_together.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="1. What other education projects are in the region?\n2. How does the budget compare to similar projects?\n3. When was the last site visit?"))]
    )
    
    rag = RAGComponents(mock_together, mock_memory)
    context = {
        "chat_history": "Previous question about CHILIPA CDSS",
        "current_answer": "Project is active with budget of 5M"
    }
    
    suggestions = rag.generate_suggestions(context)
    assert len(suggestions) == 3
    assert any("education projects" in s for s in suggestions)
    assert any("budget" in s for s in suggestions)
    assert any("site visit" in s for s in suggestions)

def test_qa_chain_creation(mock_together, mock_memory):
    rag = RAGComponents(mock_together, mock_memory)
    chain = rag.create_qa_chain()
    assert chain is not None

@pytest.mark.asyncio
async def test_full_rag_flow(mock_together, mock_memory):
    # Setup mock responses
    mock_together.chat.completions.create.side_effect = [
        # SQL generation response
        Mock(choices=[Mock(message=Mock(content="SELECT PROJECTNAME, TOTALBUDGET FROM proj_dashboard WHERE DISTRICT='Zomba'"))]),
        # Answer generation response
        Mock(choices=[Mock(message=Mock(content="There are 5 projects in Zomba with a total budget of 10M"))]),
        # Suggestions generation response
        Mock(choices=[Mock(message=Mock(content="1. What is the status of these projects?\n2. How does this compare to other districts?\n3. Which sectors are represented?"))])
    ]
    
    # Initialize components
    rag = RAGComponents(mock_together, mock_memory)
    
    # Test the full flow
    context = {
        "question": "What projects are in Zomba?",
        "sql_results": "[(Project A, 2M), (Project B, 3M)]"
    }
    
    # Generate SQL
    sql_query = rag.few_shot_prompt.format(input=context["question"])
    assert "Zomba" in sql_query
    
    # Generate answer
    answer = await rag.qa_chain.ainvoke(context)
    assert answer is not None
    assert isinstance(answer, str)
    
    # Generate suggestions
    context["current_answer"] = answer
    suggestions = rag.generate_suggestions(context)
    assert len(suggestions) == 3
    assert all(isinstance(s, str) for s in suggestions) 