import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chat_service import chat_service
from app.schemas.chat import ChatRequest, ChatResponse

client = TestClient(app)

def test_chat_endpoint():
    """Test the chat endpoint with a simple message"""
    request_data = {
        "message": "Hello, can you help me find a hotel in New York?",
        "session_id": "test_session_123"
    }
    
    response = client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "session_id" in data
    assert "timestamp" in data
    assert data["session_id"] == "test_session_123"

def test_chat_without_session_id():
    """Test chat endpoint without providing session_id"""
    request_data = {
        "message": "Hello, I need travel advice"
    }
    
    response = client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "session_id" in data
    assert "timestamp" in data
    # Should generate a new session ID
    assert data["session_id"] is not None

def test_chat_history_endpoint():
    """Test getting chat history"""
    session_id = "test_history_session"
    
    # First, send a message to create some history
    request_data = {
        "message": "Test message for history",
        "session_id": session_id
    }
    client.post("/api/chat/", json=request_data)
    
    # Then get the history
    response = client.get(f"/api/chat/history/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "session_id" in data
    assert data["session_id"] == session_id

def test_clear_chat_history():
    """Test clearing chat history"""
    session_id = "test_clear_session"
    
    # First, send a message to create some history
    request_data = {
        "message": "Test message to clear",
        "session_id": session_id
    }
    client.post("/api/chat/", json=request_data)
    
    # Then clear the history
    response = client.delete(f"/api/chat/history/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "cleared successfully" in data["message"]

def test_chat_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/api/chat/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chat"

@pytest.mark.asyncio
async def test_chat_service_process_message():
    """Test the chat service directly"""
    message = "Hello, can you help me find hotels in Paris?"
    session_id = "test_service_session"
    
    response = await chat_service.process_message(
        message=message,
        session_id=session_id
    )
    
    assert isinstance(response, ChatResponse)
    assert response.reply is not None
    assert response.session_id == session_id
    assert response.timestamp is not None

@pytest.mark.asyncio
async def test_chat_service_get_history():
    """Test getting chat history from service"""
    session_id = "test_service_history"
    
    # Add some messages first
    await chat_service.process_message("User message 1", session_id)
    await chat_service.process_message("User message 2", session_id)
    
    # Get history
    history = chat_service.get_chat_history(session_id)
    
    assert isinstance(history, list)
    assert len(history) > 0
    for message in history:
        assert message.role in ["user", "assistant"]
        assert message.content is not None 