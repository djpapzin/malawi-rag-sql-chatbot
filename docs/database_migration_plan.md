# Database Migration Plan: malawi_projects1.db to pmisProjects.db

## Objective
Replace the current database `/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db` with data from the SQL dump file `/home/dj/malawi-rag-sql-chatbot/pmisProjects.sql`, while ensuring the application works correctly with the new database structure.

## Current Status
- The application currently uses `malawi_projects1.db` for data storage
- The initialization script (`init_db.py`) generates test data rather than using real data
- The SQL dump file (`pmisProjects.sql`) contains the production data we need to use

## Migration Checklist

### 1. Database Path Updates
- [ ] Identify all files referencing the current database path
- [ ] Update all references from `malawi_projects1.db` to `pmisProjects.db`
- [ ] Verify no hardcoded paths remain in the codebase

### 2. Update Database Initialization Script
- [ ] Modify `init_db.py` to use the SQL dump file instead of generating test data
- [ ] Ensure proper error handling for SQL import
- [ ] Add validation to check if the import was successful
- [ ] Update any schema differences between the test and production databases

### 3. Data Structure Analysis
- [ ] Compare schema between current and new database
- [ ] Identify differences in table names, column names, and data types
- [ ] Document changes needed in application queries
- [ ] Update query structure in the application code if necessary

### 4. Implementation Steps
1. Create a backup of the current database
2. Modify the initialization script to import from SQL dump
3. Update database paths throughout the codebase
4. Update query structure if needed
5. Run the initialization script to create the new database
6. Test the application with the new database

### 5. Testing Plan
- [ ] Verify successful database creation from SQL dump
- [ ] Test basic application functionality
- [ ] Verify all queries work with the new database structure
- [ ] Test sample queries for each main feature
- [ ] Ensure performance is acceptable with the new database

### 6. Rollback Plan
- [ ] Keep backup of original database
- [ ] Document steps to revert changes if issues occur
- [ ] Create script to quickly switch between database versions for testing

## Technical Implementation Details

### Database Path Update Locations
The following files need to be checked and updated:
- Database connection modules
- Configuration files
- Model definitions
- Initialization scripts

### SQL Import Implementation
The new `init_db.py` will need to:
1. Connect to a new SQLite database
2. Read and parse the `pmisProjects.sql` file
3. Execute the SQL statements to create tables and import data
4. Validate the import was successful
5. Close the connection properly

### Schema Differences to Consider
- Table names may differ between test and production data
- Column naming conventions might be different
- Data types and constraints may vary
- Foreign key relationships could be more complex

## Post-Migration Verification
- Verify record counts match expected values
- Check application logs for SQL errors
- Test all features that rely on database queries
- Verify query performance with larger dataset

## Timeline
- Database path updates: 1 hour
- Initialization script modification: 2 hours
- Testing and verification: 2 hours
- Documentation updates: 1 hour
- Total estimated time: 6 hours 