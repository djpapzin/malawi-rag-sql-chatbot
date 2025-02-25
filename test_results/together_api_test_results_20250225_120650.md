# Together API Integration Test Results

Test Run: 2025-02-25 12:06:50

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
        "message": "Welcome to our Malawi infrastructure projects database! I'm thrilled to have you on board. My name is Chisomo, and I'll be your go-to assistant for all your queries about Malawi's infrastructure projects.\n\nWe've got a vast collection of data on various projects across the country, and I'm more than happy to help you navigate it. Here are some ideas to get you started:\n\n1. **District-specific projects**: Want to know about projects in a particular district, such as Lilongwe, Blantyre, or Mzuzu? Just let me know the district, and I'll provide you with a list of projects, their status, and budget allocations.\n2. **Project budgets and completion status**: Are you interested in knowing the budget allocated to a specific project or its current completion status? I can help you with that. Just provide the project name or ID, and I'll give you the details.\n3. **Sector-based projects**: Do you want to explore projects by sector, such as Infrastructure, Education, Health, or Energy? I can filter the data for you and provide a list of projects that match your criteria.\n4. **Project completion rates**: Are you curious about the overall completion rates of projects in Malawi? I can provide you with statistics on project completion rates, including the number of completed projects, their total budget, and the percentage of projects completed within the allocated timeframe.\n5. **Project timelines**: Want to know when a specific project is scheduled to start or complete? I can help you with that. Just provide the project name or ID, and I'll give you the timeline details.\n6. **Project locations**: Are you interested in knowing the exact locations of projects, including their coordinates or addresses? I can provide you with that information.\n7. **Project types**: Do you want to explore projects by type, such as road construction, bridge building, or school construction? I can filter the data for you and provide a list of projects that match your criteria.\n\nFeel free to ask me any of these questions or come up with your own queries. I'm here to help you find the information you need. What would you like to know about Malawi's infrastructure projects?"
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
    "query_type": "sql",
    "results": [
      {
        "average_age": 50.0
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "0.1s",
      "sql_query": "SELECT AVG(completionpercentage) AS average_age FROM proj_dashboard;"
    }
  }
}
```

[FAIL] Test Failed
- Expected type chat, got sql

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
        "projectname": "Lilongwe Road Development Phase 1",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 500000,
        "completionpercentage": 0,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Lilongwe School Construction Phase 3",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 987244.9,
        "completionpercentage": 10,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Lilongwe Market Development Phase 6",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 1474489.8,
        "completionpercentage": 20,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 8",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 1961734.69,
        "completionpercentage": 30,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Lilongwe Road Development Phase 11",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 2448979.59,
        "completionpercentage": 40,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Lilongwe School Construction Phase 13",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 2936224.49,
        "completionpercentage": 50,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Lilongwe Market Development Phase 16",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 3423469.39,
        "completionpercentage": 60,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 18",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 3910714.29,
        "completionpercentage": 70,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Lilongwe Road Development Phase 21",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 4397959.18,
        "completionpercentage": 80,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Lilongwe School Construction Phase 23",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 4885204.08,
        "completionpercentage": 90,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Lilongwe Market Development Phase 26",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 5372448.98,
        "completionpercentage": 100,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 28",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 5859693.88,
        "completionpercentage": 100,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Lilongwe Road Development Phase 31",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 6346938.78,
        "completionpercentage": 0,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Lilongwe School Construction Phase 33",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 6834183.67,
        "completionpercentage": 10,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Lilongwe Market Development Phase 36",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 7321428.57,
        "completionpercentage": 20,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 38",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 7808673.47,
        "completionpercentage": 30,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Lilongwe Road Development Phase 41",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 8295918.37,
        "completionpercentage": 40,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Lilongwe School Construction Phase 43",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 8783163.27,
        "completionpercentage": 50,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Lilongwe Market Development Phase 46",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 9270408.16,
        "completionpercentage": 60,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 48",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 9757653.06,
        "completionpercentage": 70,
        "startdate": 20241101,
        "completiondata": 20251101
      }
    ],
    "metadata": {
      "total_results": 20,
      "query_time": "0.1s",
      "sql_query": "SELECT projectname, projectsector, projectstatus, budget, completionpercentage, startdate, completiondata \nFROM proj_dashboard \nWHERE district = 'Lilongwe';"
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
        "message": "Welcome to the Malawi Infrastructure Projects Database. I'm here to help you navigate the various capabilities of our database. You can ask about a wide range of information related to Malawi's infrastructure projects. Here are some examples of what you can query:\n\n**1. Project Information:**\n- You can search for specific projects by their name or district.\n- You can view the sectors and status of projects, such as whether they are ongoing or completed.\n- You can check the completion percentages of projects to see how far along they are.\n\n**2. Financial Data:**\n- You can query the budgets allocated to specific projects.\n- You can get the total budgets by district or sector to see where the funds are being allocated.\n- You can compare the costs of different projects to identify areas of high expenditure.\n\n**3. Status and Progress:**\n- You can find out which projects are currently active or have been completed.\n- You can check the project timelines to see when projects are scheduled to start and finish.\n- You can view the completion rates of projects to see how well they are meeting their targets.\n\n**4. Analytics:**\n- You can get the counts of projects by district to see which areas are receiving the most investment.\n- You can calculate the average budgets of projects to see the typical cost of a project.\n- You can find the largest and smallest projects in terms of budget or scope to identify areas of high investment.\n\nThese are just a few examples of the types of information you can query in our database. If you have a specific question or need help with a particular query, feel free to ask, and I'll do my best to assist you."
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
- Timestamp: 2025-02-25 12:10:41
- Server URL: http://localhost:5000/query
