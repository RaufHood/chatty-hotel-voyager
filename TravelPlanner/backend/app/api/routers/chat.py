from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    ChatHistoryRequest, 
    ChatHistoryResponse, 
    ClearChatRequest
)
from app.services.chat_service import chat_service
from app.services.auth_deps import get_current_user
from app.services.auth_deps import get_current_user
from app.schemas.auth import User
from app.services.llm_tts_stt import stt, tts
import logging
from io import BytesIO

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Send a message to the AI travel agent.
    
    The agent will process your request and can:
    - Search for hotels using the hotel API
    - Select the best hotel based on your criteria
    - Provide travel recommendations
    - Answer questions about travel planning
    """
    try:
        # Use user ID if authenticated, otherwise use session ID
        user_id = str(current_user.id) if current_user else None
        
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get chat history for a specific session.
    """
    try:
        messages = chat_service.get_chat_history(session_id)
        return ChatHistoryResponse(
            messages=messages,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Clear chat history for a specific session.
    """
    try:
        success = chat_service.clear_chat_history(session_id)
        if success:
            return {"message": "Chat history cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear chat history")
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def chat_health():
    """
    Health check endpoint for the chat service.
    """
    return {"status": "healthy", "service": "chat"}
    

@app.post("/tts")
async def text_to_speech(payload: TTSPayload):
    try:
        text = payload.dict()['text']
        output = tts(text)
        buffer = BytesIO(output)
        return StreamingResponse(buffer, media_type="application/octet-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
        
@app.post("/stt")
async def speect_to_text(payload: UploadFile = File(...)):
    try:
        audio = await payload.read()
        output = stt(audio)
        return {"voice": output}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
