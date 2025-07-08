from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from app.services import lc_tools
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

TOOLS = [lc_tools.hotel_select_tool, 
         lc_tools.hotel_cheapest_tool, lc_tools.hotel_cxl_policy_tool, 
         lc_tools.hotel_highest_rated_tool]

SYSTEM_PROMPT = """You are TripPlanner, a professional travel agent.
When needed, call tools from the available list of tools to recommend hotels. Prioritize the user's requirements, if mentioned, else return the entire response. For every action you do, always return ONLY the structured JSON/action block response, not any natural language text."""

TOOL_TRACKER = lc_tools.ToolTracker()
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
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=session_memory,
        callbacks=[TOOL_TRACKER],
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
