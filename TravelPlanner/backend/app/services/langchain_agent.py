"""
LangChain agent using the modern LangGraph ReAct framework.
Based on latest LangChain documentation recommendations.
"""

import logging
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.services.lc_tools import TOOLS
from app.core.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatGroq(
    groq_api_key=settings.groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# System message for the ReAct agent
SYSTEM_MESSAGE = """You are TripPlanner, a helpful travel assistant with access to hotel search tools.

You have access to the following tools:
- search_and_select_hotels: Search hotels and select top 3 based on budget in one step. Use format: city=Barcelona,check_in=2025-07-08,check_out=2025-07-09,budget=150

IMPORTANT RULES:
1. ALWAYS use search_and_select_hotels - it gets real hotel data and selects the best options in one step
2. Always use the exact dates requested by the user (format: YYYY-MM-DD)
3. Always use the exact budget specified by the user
4. The system strictly respects budget constraints - if no hotels are within budget, it will inform the user
5. When no hotels are within budget, explain this clearly and offer the cheapest alternatives, or suggest to increase the distance from given location. Ask follow ups to come to agreements.
6. When hotels are found within budget, present ALL available options (up to 3) with full details
7. Do not make up hotel information - only use data from the tools

WORKFLOW:
1. Use search_and_select_hotels with the user's city, dates, and budget
2. If hotels are found within budget: Present all available options with full details
3. If no hotels are within budget: Explain this clearly and mention the cheapest alternatives

EXAMPLE:
User: "I want a hotel in Barcelona July 20-23, 2025, max 150€ per night"
You: Use search_and_select_hotels with: city=Barcelona,check_in=2025-07-20,check_out=2025-07-23,budget=150

Always provide helpful, accurate responses based on the tool results. Be transparent about budget constraints and availability."""

# Global memory for checkpointing
memory_saver = MemorySaver()

# Session-based agent storage
session_agents: Dict[str, Any] = {}

def create_agent_with_memory(session_id: str):
    """
    Create a LangGraph ReAct agent with session-based memory.
    
    Args:
        session_id: Unique identifier for the session
    
    Returns:
        LangGraph ReAct agent with checkpointing
    """
    try:
        if session_id not in session_agents:
            logger.info(f"Creating new LangGraph ReAct agent for session: {session_id}")
            
            # Create the agent using LangGraph's modern approach
            agent = create_react_agent(
                model=llm,
                tools=TOOLS,
                checkpointer=memory_saver
            )
            
            session_agents[session_id] = agent
            logger.info(f"LangGraph ReAct agent created successfully for session: {session_id}")
        
        return session_agents[session_id]
    except Exception as e:
        logger.error(f"Error creating LangGraph ReAct agent: {e}")
        raise

def get_agent():
    """Get default agent (legacy function for compatibility)"""
    return create_agent_with_memory("default_session")

class ChatMemory:
    """Session-based chat memory manager"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_or_create_agent(self, session_id: str):
        """Get or create agent for session"""
        return create_agent_with_memory(session_id)
    
    def clear_session(self, session_id: str):
        """Clear session memory"""
        if session_id in session_agents:
            del session_agents[session_id]
        logger.info(f"Cleared session: {session_id}")

# Global chat memory instance
chat_memory = ChatMemory()
