# Common Errors & Solutions

## Connection Reset Errors
```powershell
# Check server status:
Get-Process uvicorn

# Restart server:
Stop-Process -Name uvicorn -Force
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Rate Limiting
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```
Wait 60 seconds before making new requests
