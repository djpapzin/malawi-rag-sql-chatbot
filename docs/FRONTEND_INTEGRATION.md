# Frontend Integration Guide

## Required Environment Variables
```ini
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api/rag-sql-chatbot
NEXT_PUBLIC_DEFAULT_PAGE_SIZE=10
```

## API Endpoints

### Query Endpoint
```javascript
// Send a query to the chatbot
const response = await fetch('/api/rag-sql-chatbot/query', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: "What is the total budget for infrastructure projects?",
        source_lang: "english",
        page: 1,
        page_size: 30,
        continue_previous: false
    })
});

const data = await response.json();
console.log(data.response);
```

### Example Implementation
```javascript
async function sendMessage(message) {
    try {
        const response = await fetch('/api/rag-sql-chatbot/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                source_lang: 'english',
                page: 1,
                page_size: 30,
                continue_previous: false
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
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

## Response Format
The API will return responses in the following format:
```javascript
{
    response: string,    // The chatbot's response
    metadata: {
        query_time: string,
        sql_query: string,
        source: string
    }
}
