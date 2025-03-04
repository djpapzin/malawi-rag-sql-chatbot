from app.response_generator import ResponseGenerator
import pandas as pd
from datetime import datetime
import os
import csv

def save_to_markdown(content: str, filename: str):
    """Save content to a markdown file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def save_to_csv(projects_df: pd.DataFrame, filename: str):
    """Save DataFrame to CSV with proper formatting"""
    # Format currency and date columns before saving
    df_copy = projects_df.copy()
    
    # Format currency columns
    currency_columns = ['TOTALBUDGET', 'TOTALEXPENDITURETODATE']
    for col in currency_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: f"MWK {x:,.2f}" if pd.notnull(x) else "Not available")
    
    # Format date columns
    date_columns = ['STARTDATE', 'LASTVISIT']
    for col in date_columns:
        if col in df_copy.columns:
            df_copy[col] = pd.to_datetime(df_copy[col]).dt.strftime('%B %d, %Y')
    
    df_copy.to_csv(filename, index=False)

def main():
    response_generator = ResponseGenerator()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "test_results"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize markdown content
    markdown_content = f"# Response Generator Test Results\nGenerated on: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}\n\n"
    
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
    
    # General Query Example
    markdown_content += "## General Query Example\n\n```\n"
    general_result = response_generator._format_project_list(multiple_projects)
    markdown_content += general_result + "\n```\n\n"
    print("\n=== General Query Example ===")
    print(general_result)
    
    # Save general query results to CSV
    save_to_csv(multiple_projects, f"{output_dir}/general_query_{timestamp}.csv")
    
    # Specific Query Example
    markdown_content += "## Specific Query Example\n\n```\n"
    project_series = pd.Series(sample_project_data)
    specific_result = response_generator._format_specific_project(project_series)
    markdown_content += specific_result + "\n```\n\n"
    print("\n=== Specific Query Example ===")
    print(specific_result)
    
    # Save specific query results to CSV
    specific_df = pd.DataFrame([sample_project_data])
    save_to_csv(specific_df, f"{output_dir}/specific_query_{timestamp}.csv")
    
    # Pagination Example
    markdown_content += "## Pagination Example\n\n```\n"
    large_df = pd.concat([multiple_projects] * 6, ignore_index=True)  # 12 projects
    query_info = {'total_count': 15}
    pagination_result = response_generator._format_project_list(large_df[:10], query_info)
    markdown_content += pagination_result + "\n```\n\n"
    print("\n=== Pagination Example ===")
    print(pagination_result)
    
    # Save pagination results to CSV
    save_to_csv(large_df[:10], f"{output_dir}/pagination_{timestamp}.csv")
    
    # Save all results to markdown file
    save_to_markdown(markdown_content, f"{output_dir}/test_results_{timestamp}.md")
    
    print(f"\nResults have been saved to the {output_dir} directory:")
    print(f"- Markdown: test_results_{timestamp}.md")
    print(f"- CSV files:")
    print(f"  - general_query_{timestamp}.csv")
    print(f"  - specific_query_{timestamp}.csv")
    print(f"  - pagination_{timestamp}.csv")

if __name__ == '__main__':
    main() 