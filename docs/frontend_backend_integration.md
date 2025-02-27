# Frontend-Backend Integration Guide

## Overview

The Dwizani chatbot uses a modern web-based frontend that communicates with a FastAPI backend. The frontend is built with vanilla JavaScript and Tailwind CSS, providing a responsive and intuitive user interface.

## Frontend Architecture

### Directory Structure
```
frontend/
├── static/
│   ├── css/styles.css     # Tailwind CSS and custom styles
│   ├── js/main.js         # Core chat functionality
│   └── img/              # Images and icons
└── templates/
    └── index.html        # Main HTML template
```

### Key Components

1. **Chat Interface**
   - Message container with scroll functionality
   - Input form with send button
   - Loading state indicators
   - Error message display
   - Guidance tiles for common queries

2. **Message Types**
   - User messages (right-aligned)
   - Bot responses (left-aligned)
   - System messages (centered)
   - Error messages (styled in red)

## Backend Integration

### API Endpoints

1. **Main Chat Endpoint**
   ```
   POST /api/rag-sql-chatbot/chat
   Content-Type: application/json
   
   {
     "query": "string",
     "conversation_id": "string" (optional)
   }
   ```

2. **Health Check**
   ```
   GET /api/rag-sql-chatbot/health
   ```

### Error Handling

The frontend handles several types of errors:
1. Network connectivity issues
2. Server errors (500 series)
3. Invalid queries (400 series)
4. Timeout errors

### Response Format

```json
{
  "response": "string",
  "metadata": {
    "query_type": "string",
    "confidence": number,
    "processing_time": number
  },
  "error": string | null
}
```

## State Management

The chat interface maintains the following states:
1. `isLoading`: Controls loading indicator
2. `messages`: Array of chat messages
3. `error`: Current error state
4. `showGuidance`: Controls guidance tiles visibility

## Usage Example

```javascript
// Send a message to the backend
async function sendMessage(message) {
  try {
    const response = await fetch('/api/rag-sql-chatbot/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: message })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

## Best Practices

1. **Error Handling**
   - Always provide user-friendly error messages
   - Include retry mechanisms for failed requests
   - Log errors for debugging

2. **Performance**
   - Implement debouncing for rapid message sending
   - Use loading states for better UX
   - Cache responses when appropriate

3. **Accessibility**
   - Maintain ARIA labels
   - Ensure keyboard navigation
   - Provide clear focus states

4. **Mobile Responsiveness**
   - Use responsive design patterns
   - Test on various screen sizes
   - Optimize for touch interfaces
