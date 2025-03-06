# Issue Breakdown: Chatbot Response Format

## Current Issue
The chatbot system is not returning the expected structured response for specific project queries. Instead, it's returning a general "list" type response with limited fields, rather than the detailed, structured response we defined in the new `ResponseFormatter`.

## Desired Outcome
When a user asks about a specific project (e.g., "Tell me about the Nyandule Classroom Block project"), the chatbot should return a structured response with clearly defined sections and fields, such as:

- **Core Information** (Project Name, Project Code, Sector, Status, Current Stage)
- **Location** (Region, District, Traditional Authority)
- **Financial Details** (Total Budget, Expenditure to Date, Source of Funding)
- **Timeline** (Start Date, Estimated Completion Date, Last Monitoring Visit, Completion Progress)
- **Contractor Details** (Contractor, Contract Signing Date)
- **Additional Information** (Description, Fiscal Year)

However, the current response is still returning a simplified "list" format, not the structured format we defined.

## What We've Done So Far
- Updated the `QueryParser` to correctly identify specific project queries.
- Updated the SQL query generation to match the field names expected by the response formatter.
- Created and updated the `ResponseFormatter` to format responses into structured sections.
- Updated the main application (`main.py`) to use the new response formatter and database service.

## What We Need to Do Now
We need to identify why the chatbot is still returning the old "list" format instead of the structured "specific" format. The issue could be due to:

1. The main application (`app/main.py`) not correctly invoking the response formatter.
2. The response formatter (`app/response_formatter.py`) not correctly formatting the response.
3. The query parser (`app/query_parser.py`) not correctly identifying the query type as "specific".

## Next Steps
Let's carefully verify each of these components step-by-step:

1. **Check the query parser**: Ensure it correctly identifies the query as "specific".
2. Verify the main application correctly passes the query type ("specific") to the response formatter.
3. Confirm the response formatter correctly formats the response based on the query type.

I'll start by verifying the main application (`app/main.py`) to ensure it's correctly handling the response formatter invocation. 