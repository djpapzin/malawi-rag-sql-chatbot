# Security Best Practices

1. **API Key Management**:
```powershell
# Never commit .env files
Add-Content .gitignore '
# Environment files
.env
*.env.local'
```

2. **Database Credentials**:
- Rotate credentials quarterly
- Use read-only database user for API access

3. **CORS Configuration**:
```python
# app/main.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-production-domain.com"
]
```
