# Together API Integration Test Results

Test Run: 2025-02-25 12:12:03

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
        "message": "Welcome to the Malawi Infrastructure Projects Database. I'm here to help you navigate our capabilities and find the information you need.\n\n**Dataset Size:**\nWe currently have a total of 542 records in our dataset, covering various infrastructure projects across Malawi.\n\n**Capabilities:**\n\n1. **Project Information:**\n   - **Search by project name or district:** You can search for projects by their name or the district they are located in. This will give you a list of matching projects, along with their sectors and status.\n   - **View project sectors and status:** Once you have a list of projects, you can view their sectors (e.g., road, bridge, water supply) and status (e.g., active, completed, pending).\n   - **Check completion percentages:** You can also see the completion percentage for each project, giving you an idea of how far along they are.\n\n2. **Financial Data:**\n   - **Query project budgets:** You can view the budget for each project, including the total cost and any allocated funds.\n   - **Get total budgets by district/sector:** If you want to see the total budget for all projects in a particular district or sector, you can do so with our database.\n   - **Compare project costs:** You can compare the costs of different projects to identify trends or areas for improvement.\n\n3. **Status and Progress:**\n   - **Find active/completed projects:** You can filter projects by their status, showing you which ones are currently active or have been completed.\n   - **Check project timelines:** Our database includes project timelines, allowing you to see when each project is scheduled to start and end.\n   - **View completion rates:** You can view the completion rate for each project, giving you an idea of how well they are progressing.\n\n4. **Analytics:**\n   - **Get project counts by district:** You can see how many projects are located in each district, helping you understand the distribution of infrastructure projects across Malawi.\n   - **Calculate average budgets:** Our database allows you to calculate the average budget for all projects, or for specific sectors or districts.\n   - **Find largest/smallest projects:** You can identify the largest and smallest projects in terms of budget, helping you understand the scale of different infrastructure projects.\n\nFeel free to ask me any questions or request specific data, and I'll do my best to assist you."
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

[FAIL] Test Failed
- Expected type sql, got chat

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
        "message": "Welcome to our Malawi infrastructure projects database! I'm thrilled to assist you in finding the information you need. We're here to help you navigate the vast array of projects that have been implemented across Malawi.\n\nTo get started, I'd like to suggest some questions you can ask about the projects. Feel free to pick and choose the ones that interest you the most:\n\n1. **District-specific projects**: Ask about projects in specific districts, such as Lilongwe, Blantyre, Mzuzu, or any other district that's of interest to you. For example, \"What projects have been implemented in Lilongwe district?\"\n2. **Project budgets and completion status**: Query the budget allocated to a specific project and its current completion status. For instance, \"What's the budget for the M1 road upgrade project, and how far along is it?\"\n3. **Sector-specific projects**: Find projects by sector, such as infrastructure, education, healthcare, or energy. For example, \"What projects have been implemented in the education sector in Malawi?\"\n4. **Project statistics**: Get statistics about project completion rates, such as the number of projects completed, ongoing, or stalled. For instance, \"What's the completion rate for infrastructure projects in Malawi?\"\n5. **Project timelines**: Ask about the start and completion dates for specific projects. For example, \"When did the construction of the Kamuzu International Airport begin, and when is it expected to be completed?\"\n6. **Project locations**: Find projects by location, such as urban or rural areas. For instance, \"What projects have been implemented in rural areas of Malawi?\"\n7. **Project types**: Query specific types of projects, such as road construction, bridge building, or water supply systems. For example, \"What projects have been implemented to improve water supply systems in Malawi?\"\n8. **Project funding sources**: Ask about the funding sources for specific projects, such as government, donor agencies, or private sector investments. For instance, \"What's the funding source for the M1 road upgrade project?\"\n9. **Project impact**: Get information about the impact of specific projects, such as job creation, economic growth, or improved living standards. For example, \"What's the estimated impact of the Lilongwe Water Supply Project on the local economy?\"\n10. **Project trends**: Analyze trends in project implementation, such as the number of projects by sector or district over time. For instance, \"What's the trend in infrastructure project implementation in Malawi over the past 5 years?\"\n\nFeel free to ask me any of these questions or come up with your own! I'm here to help you find the information you need."
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
        "message": "I'd be happy to help you with your query. However, I need to clarify that the average age of people in the dataset is not directly related to the Malawi infrastructure projects database. The database likely contains information about projects, their characteristics, and financial data.\n\nInstead, you can ask questions that fall into the following categories:\n\n1. **Project information**:\n   - What are the names of all projects in the database?\n   - Which projects are located in a specific district or region?\n   - What are the sectors (e.g., transportation, energy, water) of the projects in the database?\n   - Can you provide a list of projects by sector?\n\n2. **Financial data**:\n   - What is the total budget for all projects in the database?\n   - Which projects have the highest and lowest budgets?\n   - What is the average cost per project?\n   - Can you provide a breakdown of costs by sector?\n\n3. **Status updates**:\n   - Which projects are currently in progress?\n   - What is the completion percentage for each project?\n   - When are the expected completion dates for each project?\n   - Can you provide a list of projects by their current status?\n\n4. **Statistics and analytics**:\n   - What is the total number of projects in the database?\n   - Which sector has the most projects?\n   - What is the average budget for projects in a specific sector?\n   - Can you provide a histogram or bar chart showing the distribution of project budgets?\n\nSome examples of supported queries might be:\n\n- \"What are the names of all projects in the transportation sector?\"\n- \"What is the total budget for all projects in the energy sector?\"\n- \"Which projects are currently in progress and have a budget over $10 million?\"\n- \"What is the average completion percentage for projects in the water sector?\"\n\nPlease let me know if you have any specific questions or if there's anything else I can help you with."
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
      "sql_query": "SELECT projectname \nFROM proj_dashboard \nWHERE district = 'Lilongwe';"
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
        "message": "Welcome to the Malawi Infrastructure Projects Database. I'm here to help you navigate and find the information you need. You can query a wide range of data related to infrastructure projects in Malawi. Here are some of the capabilities you can explore:\n\n**1. Project Information:**\n- **Search by project name or district**: Find specific projects by their name or the district where they are located.\n- **View project sectors and status**: Get an overview of the sectors (e.g., roads, bridges, water supply) and the current status (e.g., active, completed, pending) of each project.\n- **Check completion percentages**: See how far along each project is, with completion percentages indicating the progress made.\n\n**2. Financial Data:**\n- **Query project budgets**: Get detailed information about the budgets allocated to each project, including the total budget and any allocated funds.\n- **Get total budgets by district/sector**: Analyze the total budgets allocated to projects in each district or sector, providing insights into resource allocation.\n- **Compare project costs**: Compare the costs of different projects, helping you identify areas where costs can be optimized.\n\n**3. Status and Progress:**\n- **Find active/completed projects**: Identify projects that are currently active or have been completed, allowing you to track progress and plan for future projects.\n- **Check project timelines**: Get an overview of the project timelines, including start and completion dates, to help you plan and manage resources effectively.\n- **View completion rates**: See the completion rates of projects, providing insights into the efficiency of project implementation.\n\n**4. Analytics:**\n- **Get project counts by district**: Analyze the number of projects in each district, helping you identify areas with the most infrastructure development.\n- **Calculate average budgets**: Calculate the average budgets allocated to projects, providing insights into resource allocation and budgeting.\n- **Find largest/smallest projects**: Identify the largest and smallest projects in terms of budget or scope, helping you understand the scale of infrastructure development in Malawi.\n\nThese capabilities will give you a comprehensive understanding of the infrastructure projects in Malawi, enabling you to make informed decisions and plan for future development. What specific information would you like to query?"
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
- Timestamp: 2025-02-25 12:15:56
- Server URL: http://localhost:5000/query
