# Together API Integration Test Results

Test Run: 2025-02-25 12:17:44

## Test Case: Basic SQL Query

Input Message: `How many records are in the dataset?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "chat",
    "results": [
      {
        "type": "help",
        "message": "Welcome to the Malawi Infrastructure Projects Database. I'm here to help you navigate our capabilities and find the information you need.\n\n**Dataset Size:**\nWe have a total of 542 records in our dataset, covering various infrastructure projects across Malawi.\n\n**Capabilities:**\n\n1. **Project Information:**\n   - **Search by project name or district:** You can search for specific projects by name or district, making it easy to find information on a particular project.\n   - **View project sectors and status:** Get an overview of the sectors and status of each project, helping you understand the scope and progress of the projects.\n   - **Check completion percentages:** See how far along each project is, with completion percentages providing a clear picture of the project's progress.\n\n2. **Financial Data:**\n   - **Query project budgets:** Access detailed budget information for each project, including costs and expenditures.\n   - **Get total budgets by district/sector:** Analyze the total budgets allocated to projects in each district or sector, providing insights into resource allocation.\n   - **Compare project costs:** Easily compare the costs of different projects, helping you identify areas of efficiency and potential cost savings.\n\n3. **Status and Progress:**\n   - **Find active/completed projects:** Identify which projects are currently active and which have been completed, helping you track progress and plan for future projects.\n   - **Check project timelines:** View the scheduled timelines for each project, ensuring you stay on track and meet deadlines.\n   - **View completion rates:** Monitor the completion rates of projects, providing a clear picture of project success and areas for improvement.\n\n4. **Analytics:**\n   - **Get project counts by district:** Analyze the number of projects in each district, helping you understand the distribution of projects across the country.\n   - **Calculate average budgets:** Determine the average budget for projects in each sector or district, providing insights into resource allocation and project scope.\n   - **Find largest/smallest projects:** Identify the largest and smallest projects in terms of budget or scope, helping you understand the scale and complexity of projects.\n\nThese capabilities will enable you to extract valuable insights from our dataset, supporting informed decision-making and effective project management. If you have any specific questions or need help with a query, feel free to ask!"
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
        "message": "Welcome to our Malawi infrastructure projects database! I'm thrilled to have you on board. My name is Chipo, and I'll be your go-to assistant for all your queries about the projects we've listed here.\n\nWe've curated a vast collection of infrastructure projects across Malawi, covering various sectors such as transportation, energy, education, healthcare, and more. Our database is designed to provide you with valuable insights and information to help you make informed decisions or simply stay up-to-date on the latest developments.\n\nTo get started, I'd like to suggest some questions you can ask me about the projects:\n\n1. **District-specific projects**: Ask about projects in specific districts, such as Lilongwe, Blantyre, Mzuzu, or any other district you're interested in. I can provide you with a list of projects, their status, and budget allocations.\n2. **Project budgets and completion status**: Query about the budget allocated to a particular project, its current completion status, and any updates on its progress.\n3. **Sector-specific projects**: Find projects by sector, such as infrastructure, education, healthcare, or energy. I can provide you with a list of projects, their status, and budget allocations.\n4. **Project statistics**: Get statistics about project completion rates, including the number of completed projects, ongoing projects, and those that have been abandoned or delayed.\n5. **Project locations**: Ask about projects located in specific areas, such as urban or rural areas, or near specific landmarks.\n6. **Project types**: Find projects by type, such as road construction, bridge building, school construction, or hospital upgrades.\n7. **Project timelines**: Get information about project timelines, including the start and completion dates, and any notable milestones or deadlines.\n8. **Project stakeholders**: Identify the stakeholders involved in a particular project, including government agencies, private companies, NGOs, or community groups.\n\nFeel free to ask me any of these questions or anything else that's on your mind. I'm here to help you navigate our database and provide you with the information you need. What would you like to know about our Malawi infrastructure projects database?"
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

## Test Case: Invalid Query

Input Message: `What is the average age of people in the dataset?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "chat",
    "results": [
      {
        "type": "other",
        "message": "I'd be happy to help you with your query. However, I need to clarify that the average age of people in the dataset is not directly related to the Malawi infrastructure projects database. \n\nThe database appears to contain information about infrastructure projects, which typically includes details about the project name, location, sector, budget, costs, status updates, and other relevant metrics. \n\nIf you're looking for information about the people involved in these projects, such as the age of project managers, engineers, or other stakeholders, you may need to consider a different dataset or source of information.\n\nThat being said, here are some examples of questions you can ask about the Malawi infrastructure projects database:\n\n**Project Information:**\n\n* What are the names of all the projects in the database?\n* Which projects are located in the Northern Region of Malawi?\n* What are the different sectors that the projects fall under (e.g., transportation, energy, water, etc.)?\n\n**Financial Data:**\n\n* What is the total budget for all the projects in the database?\n* Which projects have a budget over $1 million?\n* What are the average costs per project?\n\n**Status Updates:**\n\n* Which projects are currently under construction?\n* What is the completion percentage for each project?\n* Which projects are expected to be completed within the next 6 months?\n\n**Statistics and Analytics:**\n\n* What is the total number of projects in the database?\n* Which sector has the most projects in the database?\n* What is the average budget for projects in the transportation sector?\n\nPlease let me know if you have any of these types of questions, and I'll do my best to assist you!"
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

## Test Case: District Query

Input Message: `Show me all projects in Lilongwe`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "sql",
    "results": [
      {
        "projectname": "Lilongwe Road Development Phase 1"
      },
      {
        "projectname": "Lilongwe School Construction Phase 3"
      },
      {
        "projectname": "Lilongwe Market Development Phase 6"
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 8"
      },
      {
        "projectname": "Lilongwe Road Development Phase 11"
      },
      {
        "projectname": "Lilongwe School Construction Phase 13"
      },
      {
        "projectname": "Lilongwe Market Development Phase 16"
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 18"
      },
      {
        "projectname": "Lilongwe Road Development Phase 21"
      },
      {
        "projectname": "Lilongwe School Construction Phase 23"
      },
      {
        "projectname": "Lilongwe Market Development Phase 26"
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 28"
      },
      {
        "projectname": "Lilongwe Road Development Phase 31"
      },
      {
        "projectname": "Lilongwe School Construction Phase 33"
      },
      {
        "projectname": "Lilongwe Market Development Phase 36"
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 38"
      },
      {
        "projectname": "Lilongwe Road Development Phase 41"
      },
      {
        "projectname": "Lilongwe School Construction Phase 43"
      },
      {
        "projectname": "Lilongwe Market Development Phase 46"
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 48"
      }
    ],
    "metadata": {
      "total_results": 20,
      "query_time": "0.1s",
      "sql_query": "SELECT projectname FROM proj_dashboard WHERE district = 'Lilongwe';"
    }
  }
}
```

[PASS] Test Passed

---

## Test Case: Budget Query

Input Message: `What is the total budget for all projects?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "sql",
    "results": [
      {
        "SUM(budget)": 1029125000.0
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "0.1s",
      "sql_query": "SELECT SUM(budget) FROM proj_dashboard;"
    }
  }
}
```

[PASS] Test Passed

---

## Test Case: General Question

Input Message: `What kind of information can I ask about?`

Status Code: 200

Response:
```json
{
  "response": {
    "query_type": "chat",
    "results": [
      {
        "type": "help",
        "message": "Welcome to the Malawi Infrastructure Projects Database. I'm here to help you navigate and find the information you need. You can ask about various aspects of the projects, including:\n\n**1. Project Information:**\nYou can query details about specific projects, such as:\n- Searching for projects by name or district\n- Viewing the sectors and status of projects\n- Checking the completion percentages of projects\n\nFor example, you can ask: \"What are the sectors and status of the 'Mulanje Road Project'?\" or \"What is the completion percentage of the 'Lilongwe Water Project'?\"\n\n**2. Financial Data:**\nYou can query financial information about projects, such as:\n- Querying project budgets\n- Getting the total budgets by district or sector\n- Comparing project costs\n\nFor example, you can ask: \"What is the budget for the 'Mulanje Road Project'?\" or \"What are the total budgets for all projects in the Lilongwe district?\"\n\n**3. Status and Progress:**\nYou can query information about the status and progress of projects, such as:\n- Finding active or completed projects\n- Checking project timelines\n- Viewing completion rates\n\nFor example, you can ask: \"What are the active projects in the Mzimba district?\" or \"What is the completion rate of the 'Lilongwe Water Project'?\"\n\n**4. Analytics:**\nYou can query analytical information about the projects, such as:\n- Getting project counts by district\n- Calculating average budgets\n- Finding the largest or smallest projects\n\nFor example, you can ask: \"How many projects are there in the Lilongwe district?\" or \"What is the average budget for all projects in the Malawi?\"\n\nYou can ask me any of these types of questions, and I'll do my best to provide you with the information you need."
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

# Test Summary

- Test file: `test_together_api.py`
- Timestamp: 2025-02-25 12:21:32
- Server URL: http://localhost:5000/query
