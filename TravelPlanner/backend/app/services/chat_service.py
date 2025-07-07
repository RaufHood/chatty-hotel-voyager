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
                }
            }
            
            # Process with LangGraph agent
            logger.info(f"Invoking LangGraph agent for session {session_id}")
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )
            
            # Extract the final response from the agent
            if result and "messages" in result:
                messages = result["messages"]
                if messages:
                    final_message = messages[-1]
                    if hasattr(final_message, 'content'):
                        response_text = final_message.content
                        logger.info(f"Agent response: {response_text[:100]}...")
                        
                        return {
                            "response": response_text,
                            "session_id": session_id,
                            "status": "success",
                            "message_count": len(messages)
                        }
            
            # Fallback if no proper response
            logger.warning(f"No valid response from agent for session {session_id}")
            return {
                "response": "I apologize, but I couldn't process your request properly. Please try again.",
                "session_id": session_id,
                "status": "error",
                "error": "No valid agent response"
            }
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    def clear_session(self, session_id: str):
        """Clear session memory"""
        self.chat_memory.clear_session(session_id)
        logger.info(f"Cleared session: {session_id}")

# Global chat service instance
chat_service = ChatService() 