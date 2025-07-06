from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage
from app.services.lc_tools import hotel_search_tool, hotel_select_tool
from langchain_groq import ChatGroq
from app.core.settings import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize the LLM
llm = ChatGroq(
    model="llama3-70b-8192",  # or "llama3-8b-8192" for smaller version
    groq_api_key=settings.groq_api_key,
    temperature=0.3,
)

TOOLS = [hotel_search_tool, hotel_select_tool]

SYSTEM_PROMPT = """You are TripPlanner, a helpful travel assistant with access to a comprehensive traveling platform. You can suggest and help book flights and hotels using specialized search tools that find accommodations and flights based on specific criteria.

When users ask about travel, gather key information through follow-up questions:
- Destination city/country
- Check-in and check-out dates (for hotels) 
- Departure and arrival dates (for flights)
- Budget range
- Number of travelers
- Specific preferences

Use the hotel_search and choose_hotel tools when you have enough information. Provide friendly, enthusiastic responses in 2-3 sentences and prioritize the user's budget and preferences."""

# Simple conversation memory for the chat agent
vector_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

class ChatMemory:
    """Custom memory class for managing chat sessions"""
    
    def __init__(self):
        self.conversations = {}
        self.agents = {}  # Store agent instances per session
    
    def add_message(self, session_id: str, message: BaseMessage):
        """Add a message to the conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append(message)
    
    def get_history(self, session_id: str) -> List[BaseMessage]:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.agents:
            del self.agents[session_id]
    
    def get_or_create_agent(self, session_id: str):
        """Get existing agent for session or create new one"""
        if session_id not in self.agents:
            self.agents[session_id] = create_agent_with_memory(session_id)
        return self.agents[session_id]

def create_agent_with_memory(session_id: str):
    """Create a new agent instance with session-specific memory"""
    # Create session-specific memory
    session_memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
    
    # Create agent with session memory
    agent = initialize_agent(
        TOOLS,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=session_memory,
        verbose=True,
    )
    
    return agent

def get_agent():
    """Get default agent with global memory (legacy function)"""
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    return initialize_agent(
        TOOLS,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=vector_memory,
        verbose=True,
    )

# Global chat memory instance
chat_memory = ChatMemory()
