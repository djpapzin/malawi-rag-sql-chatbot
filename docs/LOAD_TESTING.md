# Load Test Results

## Artillery Configuration
```yaml
config:
  target: "http://localhost:5000"
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Query endpoint stress test"
    flow:
      - post:
          url: "/api/rag-sql-chatbot/query"
          json:
            message: "List projects"
            page_size: 50
```

## Results Summary
- Max RPS: 12.3
- 95th %ile Latency: 420ms
- Error Rate: 0.2%
