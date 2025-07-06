from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    reply: str
    session_id: str
    tools_used: Optional[List[str]] = None
    hotel_data: Optional[List[Dict[str, Any]]] = None
    selected_hotel: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class ChatHistoryRequest(BaseModel):
    """Request to get chat history"""
    session_id: str

class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    messages: List[ChatMessage]
    session_id: str

class ClearChatRequest(BaseModel):
    """Request to clear chat history"""
    session_id: str 