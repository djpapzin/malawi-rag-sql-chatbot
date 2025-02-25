# Together API Integration Test Results

Test Run: 2025-02-25 12:04:11

## Test Case: Basic SQL Query

Input Message: `How many records are in the dataset?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "sql",
    "results": [
      {
        "COUNT(*)": 196
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "0.1s",
      "sql_query": "SELECT COUNT(*) FROM proj_dashboard;"
    }
  }
}
```

[PASS] Test Passed

---

## Test Case: Greeting Test

Input Message: `Hello, how are you?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "chat",
    "results": [
      {
        "type": "greeting",
        "message": "Welcome to our Malawi infrastructure projects database! I'm thrilled to have you on board. My name is Chisomo, and I'll be your go-to assistant for all your queries about Malawi's infrastructure projects.\n\nWe've curated a vast collection of projects across various sectors, including infrastructure, education, healthcare, and more. Our database is designed to provide you with valuable insights and information to help you make informed decisions.\n\nTo get started, I'd like to suggest some questions you can ask me about the projects:\n\n1. **District-specific projects**: Ask about projects in specific districts, such as Lilongwe, Blantyre, Mzuzu, or any other district you're interested in. I can provide you with a list of projects, their status, and budget allocations.\n2. **Project budgets and completion status**: Query about the budget allocations and completion status of specific projects. This will give you an idea of the project's progress and any potential challenges.\n3. **Sector-specific projects**: Find projects by sector, such as infrastructure, education, healthcare, or transportation. This will help you identify areas of focus and potential opportunities for collaboration.\n4. **Project statistics**: Get statistics about project completion rates, including the number of completed projects, ongoing projects, and those that have been abandoned or delayed.\n5. **Project locations**: Ask about projects located in specific areas, such as urban or rural areas, or near specific landmarks.\n6. **Project types**: Query about specific types of projects, such as road construction, school renovations, or hospital expansions.\n7. **Project timelines**: Get information about project timelines, including the start and end dates, and any notable milestones or deadlines.\n8. **Project stakeholders**: Identify the stakeholders involved in specific projects, including government agencies, NGOs, private companies, or community groups.\n\nFeel free to ask me any of these questions or anything else that's on your mind. I'm here to help you navigate our database and provide you with the information you need to make informed decisions. What would you like to know first?"
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "0.1s",
      "sql_query": ""
    }
  }
}
```

[PASS] Test Passed

---

## Test Case: Complex Query

Input Message: `What is the average age of people in the dataset?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "sql",
    "results": [
      {
        "AVG(completionpercentage)": 50.0
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "0.1s",
      "sql_query": "SELECT AVG(completionpercentage) FROM proj_dashboard;"
    }
  }
}
```

[PASS] Test Passed

---

# Test Summary

- Test file: `test_together_api.py`
- Timestamp: 2025-02-25 12:04:27
- Server URL: http://localhost:5000/query
