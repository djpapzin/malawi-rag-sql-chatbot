# Together API Integration Test Results

Test Run: 2025-02-25 11:56:03

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
    "query_type": "sql",
    "results": [
      {
        "projectname": "Lilongwe Road Development Phase 1",
        "district": "Lilongwe",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 500000,
        "completionpercentage": 0,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Blantyre Bridge Rehabilitation Phase 1",
        "district": "Blantyre",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 548724.49,
        "completionpercentage": 1,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Mzuzu School Construction Phase 1",
        "district": "Mzuzu",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 597448.98,
        "completionpercentage": 2,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Zomba Hospital Improvement Phase 1",
        "district": "Zomba",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 646173.47,
        "completionpercentage": 3,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Kasungu Market Development Phase 2",
        "district": "Kasungu",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 694897.96,
        "completionpercentage": 4,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Mangochi Power Plant Rehabilitation Phase 2",
        "district": "Mangochi",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 743622.45,
        "completionpercentage": 5,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Salima Water Supply Construction Phase 2",
        "district": "Salima",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 792346.94,
        "completionpercentage": 6,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Nkhata Bay Irrigation Improvement Phase 2",
        "district": "Nkhata Bay",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 841071.43,
        "completionpercentage": 7,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Karonga Road Development Phase 3",
        "district": "Karonga",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 889795.92,
        "completionpercentage": 8,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Dedza Bridge Rehabilitation Phase 3",
        "district": "Dedza",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 938520.41,
        "completionpercentage": 9,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Lilongwe School Construction Phase 3",
        "district": "Lilongwe",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 987244.9,
        "completionpercentage": 10,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Blantyre Hospital Improvement Phase 3",
        "district": "Blantyre",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 1035969.39,
        "completionpercentage": 11,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Mzuzu Market Development Phase 4",
        "district": "Mzuzu",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 1084693.88,
        "completionpercentage": 12,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Zomba Power Plant Rehabilitation Phase 4",
        "district": "Zomba",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 1133418.37,
        "completionpercentage": 13,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Kasungu Water Supply Construction Phase 4",
        "district": "Kasungu",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 1182142.86,
        "completionpercentage": 14,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Mangochi Irrigation Improvement Phase 4",
        "district": "Mangochi",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 1230867.35,
        "completionpercentage": 15,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Salima Road Development Phase 5",
        "district": "Salima",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 1279591.84,
        "completionpercentage": 16,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Nkhata Bay Bridge Rehabilitation Phase 5",
        "district": "Nkhata Bay",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 1328316.33,
        "completionpercentage": 17,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Karonga School Construction Phase 5",
        "district": "Karonga",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 1377040.82,
        "completionpercentage": 18,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Dedza Hospital Improvement Phase 5",
        "district": "Dedza",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 1425765.31,
        "completionpercentage": 19,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Lilongwe Market Development Phase 6",
        "district": "Lilongwe",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 1474489.8,
        "completionpercentage": 20,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Blantyre Power Plant Rehabilitation Phase 6",
        "district": "Blantyre",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 1523214.29,
        "completionpercentage": 21,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Mzuzu Water Supply Construction Phase 6",
        "district": "Mzuzu",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 1571938.78,
        "completionpercentage": 22,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Zomba Irrigation Improvement Phase 6",
        "district": "Zomba",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 1620663.27,
        "completionpercentage": 23,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Kasungu Road Development Phase 7",
        "district": "Kasungu",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 1669387.76,
        "completionpercentage": 24,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Mangochi Bridge Rehabilitation Phase 7",
        "district": "Mangochi",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 1718112.24,
        "completionpercentage": 25,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Salima School Construction Phase 7",
        "district": "Salima",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 1766836.73,
        "completionpercentage": 26,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Nkhata Bay Hospital Improvement Phase 7",
        "district": "Nkhata Bay",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 1815561.22,
        "completionpercentage": 27,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Karonga Market Development Phase 8",
        "district": "Karonga",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 1864285.71,
        "completionpercentage": 28,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Dedza Power Plant Rehabilitation Phase 8",
        "district": "Dedza",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 1913010.2,
        "completionpercentage": 29,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 8",
        "district": "Lilongwe",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 1961734.69,
        "completionpercentage": 30,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Blantyre Irrigation Improvement Phase 8",
        "district": "Blantyre",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 2010459.18,
        "completionpercentage": 31,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Mzuzu Road Development Phase 9",
        "district": "Mzuzu",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 2059183.67,
        "completionpercentage": 32,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Zomba Bridge Rehabilitation Phase 9",
        "district": "Zomba",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 2107908.16,
        "completionpercentage": 33,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Kasungu School Construction Phase 9",
        "district": "Kasungu",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 2156632.65,
        "completionpercentage": 34,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Mangochi Hospital Improvement Phase 9",
        "district": "Mangochi",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 2205357.14,
        "completionpercentage": 35,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Salima Market Development Phase 10",
        "district": "Salima",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 2254081.63,
        "completionpercentage": 36,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Nkhata Bay Power Plant Rehabilitation Phase 10",
        "district": "Nkhata Bay",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 2302806.12,
        "completionpercentage": 37,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Karonga Water Supply Construction Phase 10",
        "district": "Karonga",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 2351530.61,
        "completionpercentage": 38,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Dedza Irrigation Improvement Phase 10",
        "district": "Dedza",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 2400255.1,
        "completionpercentage": 39,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Lilongwe Road Development Phase 11",
        "district": "Lilongwe",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 2448979.59,
        "completionpercentage": 40,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Blantyre Bridge Rehabilitation Phase 11",
        "district": "Blantyre",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 2497704.08,
        "completionpercentage": 41,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Mzuzu School Construction Phase 11",
        "district": "Mzuzu",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 2546428.57,
        "completionpercentage": 42,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Zomba Hospital Improvement Phase 11",
        "district": "Zomba",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 2595153.06,
        "completionpercentage": 43,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Kasungu Market Development Phase 12",
        "district": "Kasungu",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 2643877.55,
        "completionpercentage": 44,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Mangochi Power Plant Rehabilitation Phase 12",
        "district": "Mangochi",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 2692602.04,
        "completionpercentage": 45,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Salima Water Supply Construction Phase 12",
        "district": "Salima",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 2741326.53,
        "completionpercentage": 46,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Nkhata Bay Irrigation Improvement Phase 12",
        "district": "Nkhata Bay",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 2790051.02,
        "completionpercentage": 47,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Karonga Road Development Phase 13",
        "district": "Karonga",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 2838775.51,
        "completionpercentage": 48,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Dedza Bridge Rehabilitation Phase 13",
        "district": "Dedza",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 2887500,
        "completionpercentage": 49,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Lilongwe School Construction Phase 13",
        "district": "Lilongwe",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 2936224.49,
        "completionpercentage": 50,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Blantyre Hospital Improvement Phase 13",
        "district": "Blantyre",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 2984948.98,
        "completionpercentage": 51,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Mzuzu Market Development Phase 14",
        "district": "Mzuzu",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 3033673.47,
        "completionpercentage": 52,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Zomba Power Plant Rehabilitation Phase 14",
        "district": "Zomba",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 3082397.96,
        "completionpercentage": 53,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Kasungu Water Supply Construction Phase 14",
        "district": "Kasungu",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 3131122.45,
        "completionpercentage": 54,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Mangochi Irrigation Improvement Phase 14",
        "district": "Mangochi",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 3179846.94,
        "completionpercentage": 55,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Salima Road Development Phase 15",
        "district": "Salima",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 3228571.43,
        "completionpercentage": 56,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Nkhata Bay Bridge Rehabilitation Phase 15",
        "district": "Nkhata Bay",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 3277295.92,
        "completionpercentage": 57,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Karonga School Construction Phase 15",
        "district": "Karonga",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 3326020.41,
        "completionpercentage": 58,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Dedza Hospital Improvement Phase 15",
        "district": "Dedza",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 3374744.9,
        "completionpercentage": 59,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Lilongwe Market Development Phase 16",
        "district": "Lilongwe",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 3423469.39,
        "completionpercentage": 60,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Blantyre Power Plant Rehabilitation Phase 16",
        "district": "Blantyre",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 3472193.88,
        "completionpercentage": 61,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Mzuzu Water Supply Construction Phase 16",
        "district": "Mzuzu",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 3520918.37,
        "completionpercentage": 62,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Zomba Irrigation Improvement Phase 16",
        "district": "Zomba",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 3569642.86,
        "completionpercentage": 63,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Kasungu Road Development Phase 17",
        "district": "Kasungu",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 3618367.35,
        "completionpercentage": 64,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Mangochi Bridge Rehabilitation Phase 17",
        "district": "Mangochi",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 3667091.84,
        "completionpercentage": 65,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Salima School Construction Phase 17",
        "district": "Salima",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 3715816.33,
        "completionpercentage": 66,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Nkhata Bay Hospital Improvement Phase 17",
        "district": "Nkhata Bay",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 3764540.82,
        "completionpercentage": 67,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Karonga Market Development Phase 18",
        "district": "Karonga",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 3813265.31,
        "completionpercentage": 68,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Dedza Power Plant Rehabilitation Phase 18",
        "district": "Dedza",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 3861989.8,
        "completionpercentage": 69,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 18",
        "district": "Lilongwe",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 3910714.29,
        "completionpercentage": 70,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Blantyre Irrigation Improvement Phase 18",
        "district": "Blantyre",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 3959438.78,
        "completionpercentage": 71,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Mzuzu Road Development Phase 19",
        "district": "Mzuzu",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 4008163.27,
        "completionpercentage": 72,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Zomba Bridge Rehabilitation Phase 19",
        "district": "Zomba",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 4056887.76,
        "completionpercentage": 73,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Kasungu School Construction Phase 19",
        "district": "Kasungu",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 4105612.24,
        "completionpercentage": 74,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Mangochi Hospital Improvement Phase 19",
        "district": "Mangochi",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 4154336.73,
        "completionpercentage": 75,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Salima Market Development Phase 20",
        "district": "Salima",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 4203061.22,
        "completionpercentage": 76,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Nkhata Bay Power Plant Rehabilitation Phase 20",
        "district": "Nkhata Bay",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 4251785.71,
        "completionpercentage": 77,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Karonga Water Supply Construction Phase 20",
        "district": "Karonga",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 4300510.2,
        "completionpercentage": 78,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Dedza Irrigation Improvement Phase 20",
        "district": "Dedza",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 4349234.69,
        "completionpercentage": 79,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Lilongwe Road Development Phase 21",
        "district": "Lilongwe",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 4397959.18,
        "completionpercentage": 80,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Blantyre Bridge Rehabilitation Phase 21",
        "district": "Blantyre",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 4446683.67,
        "completionpercentage": 81,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Mzuzu School Construction Phase 21",
        "district": "Mzuzu",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 4495408.16,
        "completionpercentage": 82,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Zomba Hospital Improvement Phase 21",
        "district": "Zomba",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 4544132.65,
        "completionpercentage": 83,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Kasungu Market Development Phase 22",
        "district": "Kasungu",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 4592857.14,
        "completionpercentage": 84,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Mangochi Power Plant Rehabilitation Phase 22",
        "district": "Mangochi",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 4641581.63,
        "completionpercentage": 85,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Salima Water Supply Construction Phase 22",
        "district": "Salima",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 4690306.12,
        "completionpercentage": 86,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Nkhata Bay Irrigation Improvement Phase 22",
        "district": "Nkhata Bay",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 4739030.61,
        "completionpercentage": 87,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Karonga Road Development Phase 23",
        "district": "Karonga",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 4787755.1,
        "completionpercentage": 88,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Dedza Bridge Rehabilitation Phase 23",
        "district": "Dedza",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 4836479.59,
        "completionpercentage": 89,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Lilongwe School Construction Phase 23",
        "district": "Lilongwe",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 4885204.08,
        "completionpercentage": 90,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Blantyre Hospital Improvement Phase 23",
        "district": "Blantyre",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 4933928.57,
        "completionpercentage": 91,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Mzuzu Market Development Phase 24",
        "district": "Mzuzu",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 4982653.06,
        "completionpercentage": 92,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Zomba Power Plant Rehabilitation Phase 24",
        "district": "Zomba",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 5031377.55,
        "completionpercentage": 93,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Kasungu Water Supply Construction Phase 24",
        "district": "Kasungu",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 5080102.04,
        "completionpercentage": 94,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Mangochi Irrigation Improvement Phase 24",
        "district": "Mangochi",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 5128826.53,
        "completionpercentage": 95,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Salima Road Development Phase 25",
        "district": "Salima",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 5177551.02,
        "completionpercentage": 96,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Nkhata Bay Bridge Rehabilitation Phase 25",
        "district": "Nkhata Bay",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 5226275.51,
        "completionpercentage": 97,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Karonga School Construction Phase 25",
        "district": "Karonga",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 5275000,
        "completionpercentage": 98,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Dedza Hospital Improvement Phase 25",
        "district": "Dedza",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 5323724.49,
        "completionpercentage": 99,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Lilongwe Market Development Phase 26",
        "district": "Lilongwe",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 5372448.98,
        "completionpercentage": 100,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Blantyre Power Plant Rehabilitation Phase 26",
        "district": "Blantyre",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 5421173.47,
        "completionpercentage": 100,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Mzuzu Water Supply Construction Phase 26",
        "district": "Mzuzu",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 5469897.96,
        "completionpercentage": 100,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Zomba Irrigation Improvement Phase 26",
        "district": "Zomba",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 5518622.45,
        "completionpercentage": 100,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Kasungu Road Development Phase 27",
        "district": "Kasungu",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 5567346.94,
        "completionpercentage": 100,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Mangochi Bridge Rehabilitation Phase 27",
        "district": "Mangochi",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 5616071.43,
        "completionpercentage": 100,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Salima School Construction Phase 27",
        "district": "Salima",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 5664795.92,
        "completionpercentage": 100,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Nkhata Bay Hospital Improvement Phase 27",
        "district": "Nkhata Bay",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 5713520.41,
        "completionpercentage": 100,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Karonga Market Development Phase 28",
        "district": "Karonga",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 5762244.9,
        "completionpercentage": 100,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Dedza Power Plant Rehabilitation Phase 28",
        "district": "Dedza",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 5810969.39,
        "completionpercentage": 100,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 28",
        "district": "Lilongwe",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 5859693.88,
        "completionpercentage": 100,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Blantyre Irrigation Improvement Phase 28",
        "district": "Blantyre",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 5908418.37,
        "completionpercentage": 100,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Mzuzu Road Development Phase 29",
        "district": "Mzuzu",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 5957142.86,
        "completionpercentage": 100,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Zomba Bridge Rehabilitation Phase 29",
        "district": "Zomba",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 6005867.35,
        "completionpercentage": 100,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Kasungu School Construction Phase 29",
        "district": "Kasungu",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 6054591.84,
        "completionpercentage": 100,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Mangochi Hospital Improvement Phase 29",
        "district": "Mangochi",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 6103316.33,
        "completionpercentage": 100,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Salima Market Development Phase 30",
        "district": "Salima",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 6152040.82,
        "completionpercentage": 100,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Nkhata Bay Power Plant Rehabilitation Phase 30",
        "district": "Nkhata Bay",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 6200765.31,
        "completionpercentage": 100,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Karonga Water Supply Construction Phase 30",
        "district": "Karonga",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 6249489.8,
        "completionpercentage": 100,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Dedza Irrigation Improvement Phase 30",
        "district": "Dedza",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 6298214.29,
        "completionpercentage": 100,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Lilongwe Road Development Phase 31",
        "district": "Lilongwe",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 6346938.78,
        "completionpercentage": 0,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Blantyre Bridge Rehabilitation Phase 31",
        "district": "Blantyre",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 6395663.27,
        "completionpercentage": 1,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Mzuzu School Construction Phase 31",
        "district": "Mzuzu",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 6444387.76,
        "completionpercentage": 2,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Zomba Hospital Improvement Phase 31",
        "district": "Zomba",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 6493112.24,
        "completionpercentage": 3,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Kasungu Market Development Phase 32",
        "district": "Kasungu",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 6541836.73,
        "completionpercentage": 4,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Mangochi Power Plant Rehabilitation Phase 32",
        "district": "Mangochi",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 6590561.22,
        "completionpercentage": 5,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Salima Water Supply Construction Phase 32",
        "district": "Salima",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 6639285.71,
        "completionpercentage": 6,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Nkhata Bay Irrigation Improvement Phase 32",
        "district": "Nkhata Bay",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 6688010.2,
        "completionpercentage": 7,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Karonga Road Development Phase 33",
        "district": "Karonga",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 6736734.69,
        "completionpercentage": 8,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Dedza Bridge Rehabilitation Phase 33",
        "district": "Dedza",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 6785459.18,
        "completionpercentage": 9,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Lilongwe School Construction Phase 33",
        "district": "Lilongwe",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 6834183.67,
        "completionpercentage": 10,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Blantyre Hospital Improvement Phase 33",
        "district": "Blantyre",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 6882908.16,
        "completionpercentage": 11,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Mzuzu Market Development Phase 34",
        "district": "Mzuzu",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 6931632.65,
        "completionpercentage": 12,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Zomba Power Plant Rehabilitation Phase 34",
        "district": "Zomba",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 6980357.14,
        "completionpercentage": 13,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Kasungu Water Supply Construction Phase 34",
        "district": "Kasungu",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 7029081.63,
        "completionpercentage": 14,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Mangochi Irrigation Improvement Phase 34",
        "district": "Mangochi",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 7077806.12,
        "completionpercentage": 15,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Salima Road Development Phase 35",
        "district": "Salima",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 7126530.61,
        "completionpercentage": 16,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Nkhata Bay Bridge Rehabilitation Phase 35",
        "district": "Nkhata Bay",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 7175255.1,
        "completionpercentage": 17,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Karonga School Construction Phase 35",
        "district": "Karonga",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 7223979.59,
        "completionpercentage": 18,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Dedza Hospital Improvement Phase 35",
        "district": "Dedza",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 7272704.08,
        "completionpercentage": 19,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Lilongwe Market Development Phase 36",
        "district": "Lilongwe",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 7321428.57,
        "completionpercentage": 20,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Blantyre Power Plant Rehabilitation Phase 36",
        "district": "Blantyre",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 7370153.06,
        "completionpercentage": 21,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Mzuzu Water Supply Construction Phase 36",
        "district": "Mzuzu",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 7418877.55,
        "completionpercentage": 22,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Zomba Irrigation Improvement Phase 36",
        "district": "Zomba",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 7467602.04,
        "completionpercentage": 23,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Kasungu Road Development Phase 37",
        "district": "Kasungu",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 7516326.53,
        "completionpercentage": 24,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Mangochi Bridge Rehabilitation Phase 37",
        "district": "Mangochi",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 7565051.02,
        "completionpercentage": 25,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Salima School Construction Phase 37",
        "district": "Salima",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 7613775.51,
        "completionpercentage": 26,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Nkhata Bay Hospital Improvement Phase 37",
        "district": "Nkhata Bay",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 7662500,
        "completionpercentage": 27,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Karonga Market Development Phase 38",
        "district": "Karonga",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 7711224.49,
        "completionpercentage": 28,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Dedza Power Plant Rehabilitation Phase 38",
        "district": "Dedza",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 7759948.98,
        "completionpercentage": 29,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 38",
        "district": "Lilongwe",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 7808673.47,
        "completionpercentage": 30,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Blantyre Irrigation Improvement Phase 38",
        "district": "Blantyre",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 7857397.96,
        "completionpercentage": 31,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Mzuzu Road Development Phase 39",
        "district": "Mzuzu",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 7906122.45,
        "completionpercentage": 32,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Zomba Bridge Rehabilitation Phase 39",
        "district": "Zomba",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 7954846.94,
        "completionpercentage": 33,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Kasungu School Construction Phase 39",
        "district": "Kasungu",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 8003571.43,
        "completionpercentage": 34,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Mangochi Hospital Improvement Phase 39",
        "district": "Mangochi",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 8052295.92,
        "completionpercentage": 35,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Salima Market Development Phase 40",
        "district": "Salima",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 8101020.41,
        "completionpercentage": 36,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Nkhata Bay Power Plant Rehabilitation Phase 40",
        "district": "Nkhata Bay",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 8149744.9,
        "completionpercentage": 37,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Karonga Water Supply Construction Phase 40",
        "district": "Karonga",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 8198469.39,
        "completionpercentage": 38,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Dedza Irrigation Improvement Phase 40",
        "district": "Dedza",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 8247193.88,
        "completionpercentage": 39,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Lilongwe Road Development Phase 41",
        "district": "Lilongwe",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 8295918.37,
        "completionpercentage": 40,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Blantyre Bridge Rehabilitation Phase 41",
        "district": "Blantyre",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 8344642.86,
        "completionpercentage": 41,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Mzuzu School Construction Phase 41",
        "district": "Mzuzu",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 8393367.35,
        "completionpercentage": 42,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Zomba Hospital Improvement Phase 41",
        "district": "Zomba",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 8442091.84,
        "completionpercentage": 43,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Kasungu Market Development Phase 42",
        "district": "Kasungu",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 8490816.33,
        "completionpercentage": 44,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Mangochi Power Plant Rehabilitation Phase 42",
        "district": "Mangochi",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 8539540.82,
        "completionpercentage": 45,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Salima Water Supply Construction Phase 42",
        "district": "Salima",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 8588265.31,
        "completionpercentage": 46,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Nkhata Bay Irrigation Improvement Phase 42",
        "district": "Nkhata Bay",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 8636989.8,
        "completionpercentage": 47,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Karonga Road Development Phase 43",
        "district": "Karonga",
        "projectsector": "Infrastructure",
        "projectstatus": "Active",
        "budget": 8685714.29,
        "completionpercentage": 48,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Dedza Bridge Rehabilitation Phase 43",
        "district": "Dedza",
        "projectsector": "Water",
        "projectstatus": "Planning",
        "budget": 8734438.78,
        "completionpercentage": 49,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Lilongwe School Construction Phase 43",
        "district": "Lilongwe",
        "projectsector": "Energy",
        "projectstatus": "Completed",
        "budget": 8783163.27,
        "completionpercentage": 50,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Blantyre Hospital Improvement Phase 43",
        "district": "Blantyre",
        "projectsector": "Education",
        "projectstatus": "On Hold",
        "budget": 8831887.76,
        "completionpercentage": 51,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Mzuzu Market Development Phase 44",
        "district": "Mzuzu",
        "projectsector": "Healthcare",
        "projectstatus": "Active",
        "budget": 8880612.24,
        "completionpercentage": 52,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Zomba Power Plant Rehabilitation Phase 44",
        "district": "Zomba",
        "projectsector": "Agriculture",
        "projectstatus": "Planning",
        "budget": 8929336.73,
        "completionpercentage": 53,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Kasungu Water Supply Construction Phase 44",
        "district": "Kasungu",
        "projectsector": "Transport",
        "projectstatus": "Completed",
        "budget": 8978061.22,
        "completionpercentage": 54,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Mangochi Irrigation Improvement Phase 44",
        "district": "Mangochi",
        "projectsector": "Infrastructure",
        "projectstatus": "On Hold",
        "budget": 9026785.71,
        "completionpercentage": 55,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Salima Road Development Phase 45",
        "district": "Salima",
        "projectsector": "Water",
        "projectstatus": "Active",
        "budget": 9075510.2,
        "completionpercentage": 56,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Nkhata Bay Bridge Rehabilitation Phase 45",
        "district": "Nkhata Bay",
        "projectsector": "Energy",
        "projectstatus": "Planning",
        "budget": 9124234.69,
        "completionpercentage": 57,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Karonga School Construction Phase 45",
        "district": "Karonga",
        "projectsector": "Education",
        "projectstatus": "Completed",
        "budget": 9172959.18,
        "completionpercentage": 58,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Dedza Hospital Improvement Phase 45",
        "district": "Dedza",
        "projectsector": "Healthcare",
        "projectstatus": "On Hold",
        "budget": 9221683.67,
        "completionpercentage": 59,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Lilongwe Market Development Phase 46",
        "district": "Lilongwe",
        "projectsector": "Agriculture",
        "projectstatus": "Active",
        "budget": 9270408.16,
        "completionpercentage": 60,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Blantyre Power Plant Rehabilitation Phase 46",
        "district": "Blantyre",
        "projectsector": "Transport",
        "projectstatus": "Planning",
        "budget": 9319132.65,
        "completionpercentage": 61,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Mzuzu Water Supply Construction Phase 46",
        "district": "Mzuzu",
        "projectsector": "Infrastructure",
        "projectstatus": "Completed",
        "budget": 9367857.14,
        "completionpercentage": 62,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Zomba Irrigation Improvement Phase 46",
        "district": "Zomba",
        "projectsector": "Water",
        "projectstatus": "On Hold",
        "budget": 9416581.63,
        "completionpercentage": 63,
        "startdate": 20230401,
        "completiondata": 20240401
      },
      {
        "projectname": "Kasungu Road Development Phase 47",
        "district": "Kasungu",
        "projectsector": "Energy",
        "projectstatus": "Active",
        "budget": 9465306.12,
        "completionpercentage": 64,
        "startdate": 20240501,
        "completiondata": 20250501
      },
      {
        "projectname": "Mangochi Bridge Rehabilitation Phase 47",
        "district": "Mangochi",
        "projectsector": "Education",
        "projectstatus": "Planning",
        "budget": 9514030.61,
        "completionpercentage": 65,
        "startdate": 20250601,
        "completiondata": 20260601
      },
      {
        "projectname": "Salima School Construction Phase 47",
        "district": "Salima",
        "projectsector": "Healthcare",
        "projectstatus": "Completed",
        "budget": 9562755.1,
        "completionpercentage": 66,
        "startdate": 20230701,
        "completiondata": 20240701
      },
      {
        "projectname": "Nkhata Bay Hospital Improvement Phase 47",
        "district": "Nkhata Bay",
        "projectsector": "Agriculture",
        "projectstatus": "On Hold",
        "budget": 9611479.59,
        "completionpercentage": 67,
        "startdate": 20240801,
        "completiondata": 20250801
      },
      {
        "projectname": "Karonga Market Development Phase 48",
        "district": "Karonga",
        "projectsector": "Transport",
        "projectstatus": "Active",
        "budget": 9660204.08,
        "completionpercentage": 68,
        "startdate": 20250901,
        "completiondata": 20260901
      },
      {
        "projectname": "Dedza Power Plant Rehabilitation Phase 48",
        "district": "Dedza",
        "projectsector": "Infrastructure",
        "projectstatus": "Planning",
        "budget": 9708928.57,
        "completionpercentage": 69,
        "startdate": 20231001,
        "completiondata": 20241001
      },
      {
        "projectname": "Lilongwe Water Supply Construction Phase 48",
        "district": "Lilongwe",
        "projectsector": "Water",
        "projectstatus": "Completed",
        "budget": 9757653.06,
        "completionpercentage": 70,
        "startdate": 20241101,
        "completiondata": 20251101
      },
      {
        "projectname": "Blantyre Irrigation Improvement Phase 48",
        "district": "Blantyre",
        "projectsector": "Energy",
        "projectstatus": "On Hold",
        "budget": 9806377.55,
        "completionpercentage": 71,
        "startdate": 20251201,
        "completiondata": 20261201
      },
      {
        "projectname": "Mzuzu Road Development Phase 49",
        "district": "Mzuzu",
        "projectsector": "Education",
        "projectstatus": "Active",
        "budget": 9855102.04,
        "completionpercentage": 72,
        "startdate": 20230101,
        "completiondata": 20240101
      },
      {
        "projectname": "Zomba Bridge Rehabilitation Phase 49",
        "district": "Zomba",
        "projectsector": "Healthcare",
        "projectstatus": "Planning",
        "budget": 9903826.53,
        "completionpercentage": 73,
        "startdate": 20240201,
        "completiondata": 20250201
      },
      {
        "projectname": "Kasungu School Construction Phase 49",
        "district": "Kasungu",
        "projectsector": "Agriculture",
        "projectstatus": "Completed",
        "budget": 9952551.02,
        "completionpercentage": 74,
        "startdate": 20250301,
        "completiondata": 20260301
      },
      {
        "projectname": "Mangochi Hospital Improvement Phase 49",
        "district": "Mangochi",
        "projectsector": "Transport",
        "projectstatus": "On Hold",
        "budget": 10001275.51,
        "completionpercentage": 75,
        "startdate": 20230401,
        "completiondata": 20240401
      }
    ],
    "metadata": {
      "total_results": 196,
      "query_time": "0.1s",
      "sql_query": "SELECT * FROM proj_dashboard;"
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
- Timestamp: 2025-02-25 11:56:54
- Server URL: http://localhost:5000/query
