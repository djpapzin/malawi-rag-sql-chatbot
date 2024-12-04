# app/utils/helpers.py
from typing import Dict, Any, List
from app.core.logger import logger  # Add logger import
from app.core.config import settings  # Add settings import

def format_project_info(project_data: Dict[str, Any]) -> str:
    """Format project information for display"""
    try:
        info = [
            f"📍 Project: {project_data['PROJECTNAME']}",
            f"  • Code: {project_data['PROJECTCODE']}",
            f"  • Type: {project_data['PROJECTTYPE']}" if project_data.get('PROJECTTYPE') else "",
            f"  • Location: {project_data['REGION']}, {project_data['DISTRICT']}",
            f"  • Sector: {project_data['PROJECTSECTOR']}",
            f"  • Status: {project_data['PROJECTSTATUS'] or 'Not specified'}",
            f"  • Funding: {project_data['FUNDINGSOURCE']}" if project_data.get('FUNDINGSOURCE') else "",
            f"  • Budget: {format_currency(project_data.get('BUDGET', 0))}",
            f"  • Completion: {project_data.get('COMPLETIONPERCENTAGE', 0)}%"
        ]
        
        # Filter out empty lines
        return "\n".join(line for line in info if line and not line.endswith(": "))
        
    except Exception as e:
        logger.error(f"Error formatting project info: {str(e)}")
        logger.error(f"Project data: {project_data}")
        return "Error formatting project information"

def analyze_question(question: str) -> Dict[str, Any]:
    """Analyze question to determine intent"""
    question_lower = question.lower()
    
    analysis = {
        "type": "general",
        "sector": None,
        "region": None,
        "status": None
    }
    
    # Use sectors from settings
    for sector, keywords in settings.SECTOR_KEYWORDS.items():
        if any(keyword in question_lower for keyword in keywords):
            analysis["sector"] = sector
    
    # Check for regions
    regions = {
        "central region": ["central", "central region"],
        "northern region": ["northern", "northern region"],
        "southern region": ["southern", "southern region"]
    }
    
    for region, keywords in regions.items():
        if any(keyword in question_lower for keyword in keywords):
            analysis["region"] = region
    
    # Check for question type
    if any(word in question_lower for word in ["how many", "count", "total"]):
        analysis["type"] = "count"
    elif any(word in question_lower for word in ["budget", "cost", "money"]):
        analysis["type"] = "budget"
    elif any(word in question_lower for word in ["complete", "progress", "status"]):
        analysis["type"] = "status"
    
    logger.debug(f"Question analysis: {analysis}")  # Add logging
    return analysis

def generate_suggestions(results: list, question: str) -> List[str]:
    """Generate contextual follow-up questions"""
    suggestions = []
    
    if not results:
        return [
            "What are the current infrastructure projects?",
            "Show me education projects",
            "What projects are in Central Region?"
        ]
    
    # Add context-specific suggestions
    if results[0].metadata.get('region'):
        suggestions.append(f"What other projects are in {results[0].metadata['region']}?")
    
    if results[0].metadata.get('sector'):
        suggestions.append(f"Show me other {results[0].metadata['sector']} projects")
    
    # Add general suggestions
    suggestions.extend([
        "Which projects have the highest completion rates?",
        "What are the major ongoing projects?"
    ])
    
    logger.debug(f"Generated suggestions: {suggestions[:3]}")  # Add logging
    return suggestions[:3]  # Return top 3 suggestions

def format_currency(amount: float) -> str:
    """Format currency values"""
    try:
        return f"MK {amount:,.2f}"
    except Exception as e:
        logger.error(f"Error formatting currency {amount}: {str(e)}")
        return "MK 0.00"