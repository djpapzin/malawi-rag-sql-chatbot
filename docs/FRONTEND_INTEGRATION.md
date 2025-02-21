# Frontend Integration Guide

## Required Environment Variables
```ini
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/rag-sql-chatbot
NEXT_PUBLIC_DEFAULT_PAGE_SIZE=10
```

## Error Handling
```javascript
// Example error handling interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 429) {
      alert('Too many requests - please wait 1 minute');
    }
    return Promise.reject(error);
  }
);
```
