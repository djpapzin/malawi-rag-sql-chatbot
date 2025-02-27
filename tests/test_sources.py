import pytest
import pandas as pd
from datetime import datetime
from app.models import QueryMetadata, QuerySource, ChatQuery, ChatResponse
from app.response_generator import ResponseGenerator
from app.sql_tracker import SQLTracker

def test_source_tracking():
    """Test SQL source tracking"""
    tracker = SQLTracker()
    
    # Test query execution with source tracking
    query = "SELECT * FROM projects WHERE sector = 'Education'"
    df, sources = tracker.execute_query(query)
    
    assert isinstance(df, pd.DataFrame)
    assert isinstance(sources, list)
    assert all(isinstance(source, QuerySource) for source in sources)
    
    # Check source details
    if sources:
        source = sources[0]
        assert hasattr(source, 'table_name')
        assert hasattr(source, 'columns')
        assert hasattr(source, 'operation')

def test_response_generation_with_sources():
    """Test response generation with source information"""
    generator = ResponseGenerator()
    
    # Create test data
    df = pd.DataFrame({
        'project_name': ['Test Project'],
        'region': ['Central'],
        'district': ['Test District'],
        'sector': ['Education'],
        'status': ['In Progress'],
        'budget': [1000000],
        'completion_percentage': [50]
    })
    
    # Create test metadata
    sources = [
        QuerySource(
            table_name='projects',
            columns=['project_name', 'region', 'district', 'sector', 'status', 'budget', 'completion_percentage'],
            operation='SELECT',
            sample_data=None
        )
    ]
    
    metadata = QueryMetadata(
        query_id='test-123',
        execution_time=0.5,
        row_count=1,
        sources=sources,
        timestamp=datetime.now()
    )
    
    # Generate response
    response = generator.generate_response(df, metadata)
    
    # Verify response structure
    assert isinstance(response, dict)
    assert 'answer' in response
    assert 'metadata' in response
    assert 'sources' in response
    
    # Verify source information
    assert isinstance(response['sources'], list)
    if response['sources']:
        source = response['sources'][0]
        assert 'table' in source
        assert 'columns' in source
        assert 'operation' in source
        assert 'sample_data' in source

def test_query_endpoint(test_client):
    """Test the query endpoint with source information"""
    # Create test query
    query = ChatQuery(
        message="Show me education projects",
        language="en"
    )
    
    # Send request
    response = test_client.post("/api/rag-sql-chatbot/chat", json=query.dict())
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert 'answer' in data
    assert 'metadata' in data
    assert 'sources' in data
    assert 'error' not in data or data['error'] is None
    
    # Verify metadata structure
    metadata = data['metadata']
    assert 'query_id' in metadata
    assert 'execution_time' in metadata
    assert 'row_count' in metadata
    assert 'timestamp' in metadata
    
    # Verify sources structure
    sources = data['sources']
    assert isinstance(sources, list)
    if sources:
        source = sources[0]
        assert 'table' in source
        assert 'columns' in source
        assert 'operation' in source
        assert 'sample_data' in source 