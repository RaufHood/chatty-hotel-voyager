import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage
from app.services.langchain_agent import chat_memory, get_agent
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.lc_tools import ToolTracker
import logging  
import json
import re

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with the LangChain agent"""
    
    def __init__(self):
        self.default_agent = get_agent()
    
    def extract_json_from_text(text: str):
        """
            Extracts the first JSON object from a string.
            Returns the parsed JSON as a dict, or raises ValueError if not found.
        """
        # This regex finds the first {...} block in the text
        match = re.search(r'\{(?:[^{}]|(?R))*\}', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in text")
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Found JSON block but failed to parse: {e}")
        
    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """Process a user message and return the agent's response"""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Create human message
            human_msg = HumanMessage(content=message)
            
            # Add to memory
            chat_memory.add_message(session_id, human_msg)
            
            # Get conversation history for context
            history = chat_memory.get_history(session_id)
            
            # Process with agent
            logger.info(f"Processing message for session {session_id}: {message[:100]}...")
            
            # Get or create session-specific agent
            agent = chat_memory.get_or_create_agent(session_id)
            
            # Run the agent with the message
            result = await agent.arun(message)
            
            # Create AI message
            ai_msg = AIMessage(content=result)
            chat_memory.add_message(session_id, ai_msg)
            
            try:
                ai_action_block = self.extract_json_from_text(result)
            except ValueError as e:
                ai_msg = AIMessage(content=f"Error extracting JSON: {e}")
            # Extract tool usage information if available
            tools_used = []
            hotel_data = []
            selected_hotel = None
            
            # Try to extract information from the agent's execution
            # This is a simplified approach - in a real implementation,
            # you might want to capture tool execution details more precisely
            
            
            # Create response
            response = ChatResponse(
                reply=ai_action_block,
                session_id=session_id,
                tools_used=tools_used if tools_used else None,
                hotel_data=hotel_data,
                selected_hotel=selected_hotel,
                timestamp=datetime.now()
            )
            
            logger.info(f"Successfully processed message for session {session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            # Return error response
            return ChatResponse(
                reply=f"I apologize, but I encountered an error while processing your request: {str(e)}",
                session_id=session_id,
                timestamp=datetime.now()
            )
    
    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        try:
            history = chat_memory.get_history(session_id)
            messages = []
            
            for msg in history:
                if isinstance(msg, HumanMessage):
                    messages.append(ChatMessage(
                        role="user",
                        content=msg.content,
                        timestamp=datetime.now()
                    ))
                elif isinstance(msg, AIMessage):
                    messages.append(ChatMessage(
                        role="assistant",
                        content=msg.content,
                        timestamp=datetime.now()
                    ))
            
            return messages
        except Exception as e:
            logger.error(f"Error getting chat history for session {session_id}: {str(e)}")
            return []
    
    def clear_chat_history(self, session_id: str) -> bool:
        """Clear chat history for a session"""
        try:
            chat_memory.clear_history(session_id)
            logger.info(f"Cleared chat history for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history for session {session_id}: {str(e)}")
            return False


# Global chat service instance
chat_service = ChatService() 