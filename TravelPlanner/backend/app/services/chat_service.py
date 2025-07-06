import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from app.core.settings import settings
from app.services.lc_tools import hotel_search
from app.schemas.chat import ChatMessage, ChatResponse
import logging
import json

logger = logging.getLogger(__name__)

class SimpleChatMemory:
    """Simple memory class for managing chat sessions"""
    
    def __init__(self):
        self.conversations = {}
    
    def add_message(self, session_id: str, message):
        """Add a message to the conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append(message)
    
    def get_history(self, session_id: str) -> List:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]

class ChatService:
    """Service for handling chat interactions with the LLM"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama3-70b-8192",
            groq_api_key=settings.groq_api_key,
            temperature=0.3,
        )
        self.memory = SimpleChatMemory()
    
    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """Process a user message and return the LLM's response"""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Processing message for session {session_id}: {message[:100]}...")
            
            # Check if the message is about hotels and use the tool if needed
            reply = ""
            tools_used = []
            hotel_data = None
            selected_hotel = None
            
            if "hotel" in message.lower() and any(city in message.lower() for city in ["paris", "london", "new york", "tokyo", "berlin", "madrid", "rome", "amsterdam", "barcelona", "vienna"]):
                # Extract city from message (simple approach)
                city = None
                cities = ["paris", "london", "new york", "tokyo", "berlin", "madrid", "rome", "amsterdam", "barcelona", "vienna"]
                for c in cities:
                    if c in message.lower():
                        city = c.title()
                        break
                
                if city:
                    try:
                        # Use the hotel search tool
                        hotels = hotel_search.func(city)
                        tools_used.append("hotel_search")
                        hotel_data = hotels
                        
                        if hotels:
                            # Create a response with hotel recommendations
                            reply = f"I found {len(hotels)} hotels in {city}:\n\n"
                            for i, hotel in enumerate(hotels[:3], 1):  # Show top 3
                                reply += f"{i}. **{hotel['name']}**\n"
                                reply += f"   - Rating: {hotel['rating']}/5\n"
                                reply += f"   - Price: ${hotel['price']}/night\n"
                                reply += f"   - Amenities: {', '.join(hotel['amenities'])}\n"
                                reply += f"   - Description: {hotel['description']}\n\n"
                            
                            # Select the best hotel
                            selected_hotel = hotels[0]  # Simple selection - first one
                            reply += f"I recommend the **{selected_hotel['name']}** as it offers great value with a {selected_hotel['rating']}/5 rating at ${selected_hotel['price']}/night."
                        else:
                            reply = f"I'm sorry, I couldn't find any hotels in {city} at the moment. Please try again later."
                    except Exception as e:
                        logger.error(f"Error using hotel search tool: {str(e)}")
                        reply = "I encountered an error while searching for hotels. Let me provide some general advice instead."
            
            # If no hotel-specific response was generated, use the LLM directly
            if not reply:
                # Get conversation history
                history = self.memory.get_history(session_id)
                
                # Create messages for the LLM
                messages = []
                
                # Add system message
                messages.append(("system", "You are TripPlanner, a helpful travel assistant. You can help users find hotels, plan trips, and provide travel advice."))
                
                # Add conversation history
                for msg in history[-10:]:  # Keep last 10 messages for context
                    if isinstance(msg, HumanMessage):
                        messages.append(("user", msg.content))
                    elif isinstance(msg, AIMessage):
                        messages.append(("assistant", msg.content))
                
                # Add current message
                messages.append(("user", message))
                
                # Get response from LLM
                result = self.llm.invoke(messages)
                reply = result.content
            
            # Store messages in memory
            human_msg = HumanMessage(content=message)
            ai_msg = AIMessage(content=reply)
            self.memory.add_message(session_id, human_msg)
            self.memory.add_message(session_id, ai_msg)
            
            # Create response
            response = ChatResponse(
                reply=reply,
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
            history = self.memory.get_history(session_id)
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
            self.memory.clear_history(session_id)
            logger.info(f"Cleared chat history for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history for session {session_id}: {str(e)}")
            return False

# Global chat service instance
chat_service = ChatService() 