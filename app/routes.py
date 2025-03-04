from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path
from app.response_generator import ResponseGenerator

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/test-responses", response_class=HTMLResponse)
async def test_responses(request: Request):
    """Test route to display response generator test results"""
    response_generator = ResponseGenerator()
    
    # Sample data (reusing from test_output.py)
    sample_project_data = {
        'PROJECTNAME': 'Lilongwe Primary School Renovation',
        'FISCALYEAR': '2023-2024',
        'DISTRICT': 'Lilongwe',
        'TOTALBUDGET': 120000000.00,
        'PROJECTSTATUS': 'In progress',
        'PROJECTSECTOR': 'Education',
        'CONTRACTORNAME': 'Malawi Construction Ltd.',
        'STARTDATE': '2023-05-15',
        'TOTALEXPENDITURETODATE': 75000000.00,
        'FUNDINGSOURCE': 'World Bank Education Grant',
        'PROJECTCODE': 'EDU-LLW-2023-005',
        'LASTVISIT': '2024-01-12'
    }
    
    # Multiple projects for general query
    multiple_projects = pd.DataFrame([
        {
            'PROJECTNAME': 'Lilongwe Primary School Renovation',
            'FISCALYEAR': '2023-2024',
            'DISTRICT': 'Lilongwe',
            'TOTALBUDGET': 120000000.00,
            'PROJECTSTATUS': 'In progress',
            'PROJECTSECTOR': 'Education'
        },
        {
            'PROJECTNAME': 'Zomba District Hospital',
            'FISCALYEAR': '2023-2024',
            'DISTRICT': 'Zomba',
            'TOTALBUDGET': 450000000.00,
            'PROJECTSTATUS': 'Planning',
            'PROJECTSECTOR': 'Health'
        }
    ])
    
    # Generate test responses
    general_response = response_generator._format_project_list(multiple_projects)
    specific_response = response_generator._format_specific_project(pd.Series(sample_project_data))
    
    # Generate pagination example
    large_df = pd.concat([multiple_projects] * 6, ignore_index=True)  # 12 projects
    query_info = {'total_count': 15}
    pagination_response = response_generator._format_project_list(large_df[:10], query_info)
    
    # Prepare test messages for display
    test_messages = [
        {
            'type': 'user',
            'content': 'Show me all projects in Lilongwe'
        },
        {
            'type': 'assistant',
            'content': general_response
        },
        {
            'type': 'user',
            'content': 'Tell me about the Lilongwe Primary School Renovation project'
        },
        {
            'type': 'assistant',
            'content': specific_response
        },
        {
            'type': 'user',
            'content': 'Show me all education projects'
        },
        {
            'type': 'assistant',
            'content': pagination_response
        }
    ]
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "messages": test_messages,
            "test_mode": True
        }
    ) 