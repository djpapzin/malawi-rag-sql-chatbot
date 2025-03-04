from app.response_generator import ResponseGenerator
import pandas as pd

def main():
    response_generator = ResponseGenerator()
    
    # Sample data
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
    
    # Test general query (multiple projects)
    print("\n=== General Query Example ===")
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
    print(response_generator._format_project_list(multiple_projects))
    
    # Test specific query
    print("\n=== Specific Query Example ===")
    project_series = pd.Series(sample_project_data)
    print(response_generator._format_specific_project(project_series))
    
    # Test pagination
    print("\n=== Pagination Example ===")
    large_df = pd.concat([multiple_projects] * 6, ignore_index=True)  # 12 projects
    query_info = {'total_count': 15}
    print(response_generator._format_project_list(large_df[:10], query_info))

if __name__ == '__main__':
    main() 