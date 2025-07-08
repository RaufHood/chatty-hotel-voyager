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
- search_and_select_hotels: Search hotels and select top 3 based on budget in one step. Requires: city (string), check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), budget (integer)

IMPORTANT RULES:
1. ONLY use hotel search tools when the user explicitly asks for hotel recommendations, searches, or bookings
2. For simple greetings like "hi", "hello", "hey" - respond conversationally without using any tools
3. For general questions about travel - provide helpful information without automatically searching hotels
4. ONLY search hotels when the user mentions: hotels, accommodation, stay, booking, or similar travel-related requests
5. When using search_and_select_hotels, always require the user to specify or ask for: city, dates, and budget
6. Do not make assumptions or use default values unless the user explicitly says they're flexible

WHEN TO USE TOOLS:
✅ "Find hotels in Barcelona" - Use tools
✅ "I need accommodation in Paris" - Use tools  
✅ "Book a hotel for next week" - Use tools
✅ "Show me hotels under 200€" - Use tools
❌ "Hi" - Just greet back, no tools
❌ "Hello" - Just greet back, no tools
❌ "How are you?" - Answer conversationally, no tools
❌ "What can you do?" - Explain capabilities, no tools

DATE HANDLING (only when user requests hotels):
- If user says "anytime", "any date", "flexible" - ask them to specify preferred dates
- If user gives specific dates, use those exactly
- If user says "next week", calculate the actual dates
- CURRENT YEAR: Always use 2025 for dates unless user specifies otherwise
- DATE EXAMPLES: "29th-30th July" = 2025-07-29 to 2025-07-30, "July 29-30" = 2025-07-29 to 2025-07-30
- Format dates as YYYY-MM-DD (e.g., 2025-07-29, 2025-07-30)
- IMPORTANT: Parse relative dates like "29th-30th July" as check-in=2025-07-29, check-out=2025-07-30

BUDGET HANDLING (only when user requests hotels):
- If user specifies budget, use it exactly
- If no budget specified, ask the user for their budget preference
- Do not assume default budgets

CONTEXT AND MEMORY:
- ALWAYS read and use the full conversation history before responding
- If user mentioned city, dates, or budget in previous messages, USE THAT INFORMATION
- Do not ask for information the user already provided in the conversation
- Remember the conversation context and build upon it

WORKFLOW FOR HOTEL REQUESTS:
1. Check if user is actually asking for hotels/accommodation
2. Review conversation history for any previously mentioned: city, dates, budget
3. If you have all required info (city, dates, budget) from conversation history, proceed with search
4. If missing any of these, ask the user ONLY for the missing information
5. Use search_and_select_hotels tool with structured parameters
6. Present results clearly with full details

Always provide helpful, accurate responses. Be conversational for greetings and general questions. Only use tools when the user specifically requests hotel-related services."""

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
                prompt=SYSTEM_MESSAGE,
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
