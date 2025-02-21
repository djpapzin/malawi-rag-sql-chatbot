from typing import List, Dict, Any, Optional
from decimal import Decimal
import uuid
from datetime import datetime

from .models import (
    GeneralQueryResponse, SpecificQueryResponse,
    ProjectGeneral, ProjectSpecific,
    Location, MonetaryValue, ContractorInfo,
    Summary, ResponseMetadata,
    format_currency, format_date
)

def create_monetary_value(amount: float) -> MonetaryValue:
    """Create a MonetaryValue object from a float amount"""
    decimal_amount = Decimal(str(amount))
    return MonetaryValue(
        amount=decimal_amount,
        formatted=format_currency(decimal_amount)
    )

def create_location(region: str, district: str) -> Location:
    """Create a Location object"""
    return Location(
        region=region,
        district=district
    )

def create_contractor_info(name: str, start_date: str) -> ContractorInfo:
    """Create a ContractorInfo object"""
    return ContractorInfo(
        name=name,
        contract_start_date=format_date(start_date)
    )

def format_general_response(query_results: List[Dict[str, Any]]) -> GeneralQueryResponse:
    """Format a general query response"""
    projects = []
    total_budget = Decimal('0')

    for result in query_results:
        budget = Decimal(str(result.get('budget', 0)))
        total_budget += budget

        project = ProjectGeneral(
            project_name=result.get('projectname', ''),
            fiscal_year=result.get('fiscalyear', ''),
            location=create_location(
                result.get('region', ''),
                result.get('district', '')
            ),
            budget=create_monetary_value(budget),
            status=result.get('projectstatus', ''),
            sector=result.get('projectsector', '')
        )
        projects.append(project)

    summary = Summary(
        total_projects=len(projects),
        total_budget=create_monetary_value(total_budget)
    )

    metadata = ResponseMetadata(
        query_id=str(uuid.uuid4())
    )

    return GeneralQueryResponse(
        results=projects,
        summary=summary,
        metadata=metadata
    )

def format_specific_response(result: Dict[str, Any]) -> SpecificQueryResponse:
    """Format a specific query response"""
    budget = Decimal(str(result.get('budget', 0)))
    expenditure = Decimal(str(result.get('expenditure_to_date', 0)))

    project = ProjectSpecific(
        project_name=result.get('projectname', ''),
        fiscal_year=result.get('fiscalyear', ''),
        location=create_location(
            result.get('region', ''),
            result.get('district', '')
        ),
        budget=create_monetary_value(budget),
        status=result.get('projectstatus', ''),
        sector=result.get('projectsector', ''),
        contractor=create_contractor_info(
            result.get('contractor_name', ''),
            result.get('contract_start_date', '')
        ),
        expenditure_to_date=create_monetary_value(expenditure),
        funding_source=result.get('funding_source', ''),
        project_code=result.get('project_code', ''),
        last_monitoring_visit=format_date(result.get('last_monitoring_visit', ''))
    )

    metadata = ResponseMetadata(
        query_id=str(uuid.uuid4())
    )

    return SpecificQueryResponse(
        result=project,
        metadata=metadata
    )

def is_specific_query(query: str) -> bool:
    """Determine if a query is asking for specific project details"""
    specific_keywords = [
        'details', 'specific', 'tell me more about', 'show me details',
        'contractor', 'expenditure', 'monitoring', 'funding source'
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in specific_keywords) 