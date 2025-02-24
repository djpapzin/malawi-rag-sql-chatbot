import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# Read the CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, 'query_analysis_sample.csv'))

# Add query type classification
def classify_query(row):
    if 'project_name' in row and row['project_name']:
        return 'Specific'
    return 'General'

df['QueryType'] = df.apply(classify_query, axis=1)

# Set style
plt.style.use('seaborn')
sns.set_palette("husl")

# Create output directory for plots
plots_dir = 'plots'
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# 1. Category Performance Plot
plt.figure(figsize=(12, 6))
category_performance = df.groupby('Category')['Match %'].mean()
ax = category_performance.plot(kind='bar')
plt.title('Match Rate by Query Category')
plt.xlabel('Query Category')
plt.ylabel('Average Match Rate (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'category_performance.png'))
plt.close()

# 2. Response Time Distribution
plt.figure(figsize=(10, 6))
sns.boxplot(x='Category', y='Response Time', data=df)
plt.title('Response Time Distribution by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'response_time_distribution.png'))
plt.close()

# 3. Match Rate Distribution
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Match %', bins=20)
plt.title('Distribution of Match Rates')
plt.xlabel('Match Rate (%)')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'match_rate_distribution.png'))
plt.close()

# 4. API vs DB Results Comparison
plt.figure(figsize=(12, 6))
plt.scatter(df['API Results'], df['DB Matches'])
plt.plot([0, df['API Results'].max()], [0, df['API Results'].max()], 'r--')
plt.title('API Results vs Database Matches')
plt.xlabel('API Results')
plt.ylabel('Database Matches')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'api_vs_db_comparison.png'))
plt.close()

# 1. Query Type Performance Plot
plt.figure(figsize=(10, 6))
type_performance = df.groupby('QueryType')['Match %'].mean()
ax = type_performance.plot(kind='bar')
plt.title('Match Rate by Query Type')
plt.xlabel('Query Type')
plt.ylabel('Average Match Rate (%)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'query_type_performance.png'))
plt.close()

# 2. Project Drill-Down Analysis
project_stats = pd.DataFrame({
    'Project': df[df['QueryType'] == 'Specific']['project_name'].unique(),
    'Query Count': df[df['QueryType'] == 'Specific'].groupby('project_name').size(),
    'Avg Match Rate': df[df['QueryType'] == 'Specific'].groupby('project_name')['Match %'].mean(),
    'Avg Response Time': df[df['QueryType'] == 'Specific'].groupby('project_name')['Response Time'].mean()
}).sort_values('Query Count', ascending=False)

# Save project stats
project_stats.to_csv(os.path.join(plots_dir, 'project_statistics.csv'))

# 3. Project Query Performance
plt.figure(figsize=(12, 6))
top_projects = project_stats.head(10)  # Top 10 most queried projects
sns.barplot(data=top_projects, x='Project', y='Avg Match Rate')
plt.title('Match Rate for Most Queried Projects')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'project_match_rates.png'))
plt.close()

# Generate summary statistics
summary_stats = pd.DataFrame({
    'Category': df['Category'].unique(),
    'Avg Match Rate': df.groupby('Category')['Match %'].mean(),
    'Avg Response Time': df.groupby('Category')['Response Time'].mean(),
    'Query Count': df.groupby('Category').size()
})

# Save summary statistics
summary_stats.to_csv(os.path.join(plots_dir, 'summary_statistics.csv'))

# Generate summary markdown
project_summary = """
## Project-Specific Analysis

### Query Type Performance
![Query Type Performance](plots/query_type_performance.png)
- Compares performance between specific project queries and general queries
- Shows which query type provides more accurate results

### Top Projects Analysis
![Project Match Rates](plots/project_match_rates.png)
- Shows match rates for the most frequently queried projects
- Helps identify which projects have consistent results

### Project-Specific Statistics

| Project | Query Count | Avg Match Rate (%) | Avg Response Time (s) |
|---------|-------------|-------------------|---------------------|
"""

# Add top 10 projects to summary
for _, row in top_projects.iterrows():
    project_summary += f"| {row['Project']} | {row['Query Count']} | {row['Avg Match Rate']:.1f} | {row['Avg Response Time']:.2f} |\n"

project_summary += """
### Query Type Breakdown

| Query Type | Count | Avg Match Rate (%) | Avg Response Time (s) |
|------------|-------|-------------------|---------------------|
"""

# Add query type stats
type_stats = df.groupby('QueryType').agg({
    'Match %': 'mean',
    'Response Time': 'mean',
    'Query': 'count'
}).round(2)

for qtype, row in type_stats.iterrows():
    project_summary += f"| {qtype} | {row['Query']} | {row['Match %']:.1f} | {row['Response Time']:.2f} |\n"

# Generate visualization section
viz_section = """
## Visualization Analysis

### 1. Category Performance
![Category Performance](plots/category_performance.png)
- Shows average match rates across different query categories
- Highlights which types of queries perform best

### 2. Response Time Analysis
![Response Time Distribution](plots/response_time_distribution.png)
- Displays response time distribution by category
- Helps identify any performance bottlenecks

### 3. Match Rate Distribution
![Match Rate Distribution](plots/match_rate_distribution.png)
- Shows the distribution of match rates across all queries
- Helps identify if results tend to be too broad or too narrow

### 4. API vs Database Comparison
![API vs DB Comparison](plots/api_vs_db_comparison.png)
- Compares API results with actual database matches
- Helps identify discrepancies between API responses and database content

"""

# Read existing report
with open('chatbot_query_analysis_report.md', 'r', encoding='utf-8') as f:
    report_content = f.read()

# Insert project summary and visualization section before "Next Steps"
report_content = report_content.replace('## Next Steps', project_summary + '\n\n' + viz_section + '\n## Next Steps')

# Save updated report
with open('chatbot_query_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

import pandas as pd
import matplotlib.pyplot as plt
import json

def analyze_queries():
    # Load data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(script_dir, 'query_analysis_sample.csv'))
    
    # Classify queries
    def classify_query(query):
        query = query.lower()
        if any(term in query for term in ['show me', 'what is', 'tell me about']):
            if 'project' in query and any(code in query for code in ['mw-cr-do', 'mw-sr-bt']):
                return 'project_code'
            elif any(proj in query for proj in ['nachuma market', 'boma bus depot', 'chilipa cdss']):
                return 'specific_project'
        if any(term in query for term in ['in zomba', 'in mchinji', 'in southern region']):
            return 'location_based'
        if any(term in query for term in ['completed', 'ongoing', 'delayed']):
            return 'status_based'
        return 'general'
    
    df['query_type'] = df['query'].apply(classify_query)
    
    # Calculate metrics by query type
    query_metrics = df.groupby('query_type').agg({
        'match_rate': ['mean', 'count'],
        'response_time': 'mean'
    }).round(2)
    
    # Generate summary report
    report_path = os.path.join(script_dir, 'query_analysis_summary.md')
    with open(report_path, 'w') as f:
        f.write('# Query Analysis Summary\n\n')
        
        f.write('## Query Type Performance\n\n')
        f.write('| Query Type | Count | Avg Match Rate (%) | Avg Response Time (s) |\n')
        f.write('|------------|--------|-------------------|---------------------|\n')
        
        for query_type in query_metrics.index:
            count = query_metrics.loc[query_type, ('match_rate', 'count')]
            match_rate = query_metrics.loc[query_type, ('match_rate', 'mean')]
            response_time = query_metrics.loc[query_type, 'response_time']
            f.write(f'| {query_type} | {count} | {match_rate:.1f} | {response_time:.2f} |\n')
        
        f.write('\n## Sample Queries\n\n')
        for query_type in df['query_type'].unique():
            f.write(f'\n### {query_type.title()} Queries\n\n')
            type_queries = df[df['query_type'] == query_type]
            for _, row in type_queries.iterrows():
                f.write(f'- "{row["query"]}"\n')
                f.write(f'  - Match Rate: {row["match_rate"]}%\n')
                f.write(f'  - Response Time: {row["response_time"]}s\n')

if __name__ == '__main__':
    analyze_queries()
    print("Analysis complete! Check results/query_analysis_summary.md for the report.")

print("Visualizations and updated report generated successfully!")
