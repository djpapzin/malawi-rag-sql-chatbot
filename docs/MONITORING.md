# Monitoring Configuration

## Prometheus Metrics Endpoint
```python
# Add to app/main.py
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

## Key Metrics Tracked
- `api_requests_total`
- `query_processing_time_seconds`
- `database_query_duration_seconds`

## Grafana Dashboard Setup
```powershell
# Import dashboard template
grafana-cli admin reset-admin-password admin
grafana-cli plugins install grafana-simple-json-datasource
```
