# Database Schema

## Projects Table
```sql
CREATE TABLE proj_dashboard (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    fiscal_year INTEGER,
    region TEXT,
    district TEXT,
    total_budget REAL,
    project_status TEXT CHECK(status IN ('Active','Completed')),
    sector TEXT
);
```

## Query History
```sql
CREATE TABLE query_history (
    query_id UUID PRIMARY KEY,
    timestamp DATETIME,
    raw_query TEXT,
    generated_sql TEXT,
    execution_time_ms INTEGER
);
```
