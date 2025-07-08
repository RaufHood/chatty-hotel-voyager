"""
Chat service using modern LangGraph ReAct agent.
"""

import logging
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from app.services.langchain_agent import chat_memory

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with LangGraph ReAct agent"""
    
    def __init__(self):
        self.chat_memory = chat_memory
    
    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a chat message using LangGraph ReAct agent.
        
        Args:
            session_id: Unique session identifier
            message: User message
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            logger.info(f"Processing message for session {session_id}: {message[:100]}...")
            
            # Get or create agent for this session
            agent = self.chat_memory.get_or_create_agent(session_id)
            
            # Create configuration for the agent with session thread
            config = {
                "configurable": {
                    "thread_id": session_id
                },
                "recursionLimit": 8  # Limit to 8 steps to prevent infinite loops
            }
            
            # Process with LangGraph agent
            logger.info(f"Invoking LangGraph agent for session {session_id}")
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )
            
            # Get hotel data from global storage (set by tools)
            from app.services.lc_tools import get_last_hotel_cards
            hotel_data = get_last_hotel_cards()
            
            # Extract the final response from the agent
            if result and "messages" in result:
                messages = result["messages"]
                if messages:
                    final_message = messages[-1]
                    if hasattr(final_message, 'content'):
                        response_text = final_message.content
                        logger.info(f"Agent response: {response_text[:100]}...")
                        
                        if hotel_data:
                            logger.info(f"Found {len(hotel_data)} hotel cards to display")
                        
                        return {
                            "reply": response_text,
                            "session_id": session_id,
                            "status": "success",
                            "message_count": len(messages),
                            "hotel_data": hotel_data
                        }
            
            # Fallback if no proper response
            logger.warning(f"No valid response from agent for session {session_id}")
            return {
                "reply": "I apologize, but I couldn't process your request properly. Please try again.",
                "session_id": session_id,
                "status": "error",
                "error": "No valid agent response"
            }
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            return {
                "reply": "I apologize, but I encountered an error processing your request. Please try again.",
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    def clear_session(self, session_id: str):
        """Clear session memory"""
        self.chat_memory.clear_session(session_id)
        logger.info(f"Cleared session: {session_id}")
    
    def _extract_hotel_cards(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract frontend hotel cards from agent response"""
        import json
        import re
        
        try:
            # Find JSON objects in the response that contain frontend_hotel_cards
            json_pattern = r'\{[^{}]*"frontend_hotel_cards"[^{}]*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            for match in matches:
                try:
                    # Try to parse as JSON
                    data = json.loads(match)
                    if "frontend_hotel_cards" in data:
                        return data["frontend_hotel_cards"]
                except json.JSONDecodeError:
                    continue
            
            # Fallback: look for the specific pattern more broadly
            start_marker = '"frontend_hotel_cards": ['
            if start_marker in response_text:
                start_idx = response_text.find(start_marker) + len('"frontend_hotel_cards": ')
                # Find the matching bracket
                bracket_count = 0
                end_idx = start_idx
                for i, char in enumerate(response_text[start_idx:]):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = start_idx + i + 1
                            break
                
                hotel_json = response_text[start_idx:end_idx]
                return json.loads(hotel_json)
            
        except Exception as e:
            logger.error(f"Error extracting hotel cards: {e}")
        
        return None

# Global chat service instance
chat_service = ChatService() 