# Chat API Documentation

The Chat API provides an AI-powered travel assistant that can help users with travel planning, hotel searches, and travel recommendations.

## Features

- **AI Travel Agent**: Powered by LangChain and Groq LLM
- **Hotel Search**: Integration with hotel APIs to find accommodations
- **Conversation Memory**: Maintains chat history for context
- **Session Management**: Support for multiple chat sessions
- **Authentication**: Optional user authentication for personalized experiences

## API Endpoints

### 1. Send Message
**POST** `/api/chat/`

Send a message to the AI travel agent.

**Request Body:**
```json
{
  "message": "I need a hotel in Paris for next week",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "reply": "I'll help you find hotels in Paris! Let me search for some options...",
  "session_id": "generated-or-provided-session-id",
  "tools_used": ["hotel_search"],
  "hotel_data": [...],
  "selected_hotel": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Get Chat History
**GET** `/api/chat/history/{session_id}`

Retrieve the conversation history for a specific session.

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need a hotel in Paris",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant", 
      "content": "I found several hotels in Paris...",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "session_id": "session-id"
}
```

### 3. Clear Chat History
**DELETE** `/api/chat/history/{session_id}`

Clear the conversation history for a specific session.

**Response:**
```json
{
  "message": "Chat history cleared successfully"
}
```

### 4. Health Check
**GET** `/api/chat/health`

Check the health status of the chat service.

**Response:**
```json
{
  "status": "healthy",
  "service": "chat"
}
```

## AI Agent Capabilities

The AI agent can:

1. **Search for Hotels**: Use the `hotel_search` tool to find hotels by city and dates
2. **Select Best Hotels**: Use the `choose_hotel` tool to pick the best hotel based on criteria
3. **Provide Travel Advice**: Answer questions about destinations, travel tips, etc.
4. **Maintain Context**: Remember previous conversation for better assistance

## Example Conversations

### Hotel Search
```
User: "I need a hotel in New York for March 15-20, 2024"
Agent: "I'll search for hotels in New York for your dates. Let me find some options for you..."
[Agent uses hotel_search tool]
Agent: "I found several hotels in New York. Here are the top options..."
```

### Travel Planning
```
User: "What's the best time to visit Tokyo?"
Agent: "The best time to visit Tokyo depends on what you're looking for. Spring (March-May) is popular for cherry blossoms..."
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# AI/LLM Settings
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional backup

# Hotel API Settings (when integrating real hotel API)
HOTEL_API_KEY=your_hotel_api_key_here
HOTEL_API_URL=https://api.hoteloperations.com
```

### Dependencies

The chat functionality requires these additional packages:
- `langchain>=0.0.350`
- `langchain-community>=0.0.10`
- `langchain-groq>=0.0.1`

## Error Handling

The API includes comprehensive error handling:

- **500 Internal Server Error**: When the AI agent encounters an error
- **400 Bad Request**: When request data is invalid
- **401 Unauthorized**: When authentication is required but not provided

## Testing

Run the chat API tests:

```bash
cd backend
pytest app/tests/test_chat.py -v
```

## Integration with Frontend

The chat API is designed to work seamlessly with frontend applications:

1. **Session Management**: Use the returned `session_id` to maintain conversation context
2. **Real-time Updates**: The API supports streaming responses for real-time chat
3. **Authentication**: Optional user authentication for personalized experiences
4. **Error Handling**: Comprehensive error responses for frontend error handling

## Future Enhancements

- [ ] Real-time WebSocket support for live chat
- [ ] Integration with real hotel booking APIs
- [ ] Multi-language support
- [ ] Voice chat capabilities
- [ ] Advanced conversation analytics
- [ ] Integration with flight search APIs 