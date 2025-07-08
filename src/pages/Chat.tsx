import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ArrowLeft, Menu, Mic, MicOff, Plus } from "lucide-react";
import { ChatMessage } from "@/components/ChatMessage";
import { HotelResults } from "@/components/HotelResults";
import { ChatSidebar } from "@/components/ChatSidebar";
import { useVoiceRecording } from "@/hooks/use-voice-recording";
import { apiService, ChatRequest } from "@/services/api";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  hotelData?: any[];
  selectedHotel?: any;
  autoPlayTTS?: boolean;
  isVoiceMessage?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  lastMessage?: string;
  createdAt: string;
  updatedAt: string;
}

// Chat persistence utilities
const CHAT_SESSIONS_KEY = 'chatSessions';
const CURRENT_SESSION_KEY = 'currentChatSession';

const saveChatSession = (session: ChatSession) => {
  try {
    const sessions = getChatSessions();
    const existingIndex = sessions.findIndex(s => s.id === session.id);
    
    if (existingIndex >= 0) {
      sessions[existingIndex] = session;
    } else {
      sessions.unshift(session); // Add new sessions at the beginning
    }
    
    // Keep only last 50 sessions
    if (sessions.length > 50) {
      sessions.splice(50);
    }
    
    localStorage.setItem(CHAT_SESSIONS_KEY, JSON.stringify(sessions));
    localStorage.setItem(CURRENT_SESSION_KEY, session.id);
  } catch (error) {
    console.error('Error saving chat session:', error);
  }
};

const getChatSessions = (): ChatSession[] => {
  try {
    const sessions = localStorage.getItem(CHAT_SESSIONS_KEY);
    return sessions ? JSON.parse(sessions) : [];
  } catch (error) {
    console.error('Error loading chat sessions:', error);
    return [];
  }
};

const getChatSession = (sessionId: string): ChatSession | null => {
  try {
    const sessions = getChatSessions();
    return sessions.find(s => s.id === sessionId) || null;
  } catch (error) {
    console.error('Error loading chat session:', error);
    return null;
  }
};

const getCurrentSessionId = (): string | null => {
  try {
    return localStorage.getItem(CURRENT_SESSION_KEY);
  } catch (error) {
    return null;
  }
};

const generateSessionTitle = (firstMessage: string): string => {
  // Extract key words from the first message to create a title
  const cleanMessage = firstMessage.toLowerCase().replace(/[^\w\s]/g, '');
  const words = cleanMessage.split(' ').filter(word => word.length > 2);
  
  if (words.length === 0) return 'New Chat';
  
  // Look for location names or travel-related keywords
  const importantWords = words.filter(word => 
    ['hotel', 'hotels', 'trip', 'travel', 'vacation', 'book', 'booking', 'find', 'search'].includes(word) ||
    word.length > 4
  );
  
  const title = importantWords.slice(0, 3).join(' ');
  return title.charAt(0).toUpperCase() + title.slice(1) || 'New Chat';
};

const Chat = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sessionId } = useParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Generate a session ID if not provided
  const [currentSessionId] = useState(() => {
    if (sessionId) return sessionId;
    
    // If there's an initial message, always create a new session
    if (location.state?.initialMessage) {
      return `session_${Date.now()}`;
    }
    
    // For new chat (no sessionId and no initial message), always create new session
    // Don't try to load existing session from localStorage for new chats
    return `session_${Date.now()}`;
  });
  
  const { 
    isRecording, 
    startRecording, 
    stopRecording, 
    error: recordingError 
  } = useVoiceRecording();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat session on component mount
  useEffect(() => {
    const loadChatSession = () => {
      const initialMessage = location.state?.initialMessage;
      
      if (initialMessage && !sessionId) {
        // New chat with initial message
        const userMessage: Message = {
          id: Date.now().toString(),
          content: initialMessage,
          role: "user",
          timestamp: new Date(),
        };
        
        setMessages([userMessage]);
        setIsLoading(true);
        
        // Send the initial message to the backend
        sendMessageToBackend(initialMessage);
      } else if (sessionId) {
        // Load existing session
        const session = getChatSession(sessionId);
        if (session) {
          // Convert timestamp strings back to Date objects
          const messagesWithDates = session.messages.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }));
          setMessages(messagesWithDates);
        } else {
          // Session not found, show welcome message
          setMessages([
            {
              id: "1",
              content: "Hi! I'm your travel assistant. Tell me about your ideal trip - where would you like to go and when?",
              role: "assistant",
              timestamp: new Date(),
            }
          ]);
        }
      } else {
        // New chat without sessionId - always start fresh
        // Clear any existing current session since this is a new chat
        localStorage.removeItem(CURRENT_SESSION_KEY);
        
        // Show welcome message for new chats
        setMessages([
          {
            id: "1",
            content: "Hi! I'm your travel assistant. Tell me about your ideal trip - where would you like to go and when?",
            role: "assistant",
            timestamp: new Date(),
          }
        ]);
      }
    };

    loadChatSession();
  }, [location.state, sessionId]);

  // Save chat session whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      // Don't save if it's just the welcome message
      if (messages.length === 1 && messages[0].role === "assistant" && messages[0].id === "1") {
        return;
      }
      
      // Generate title from first user message
      const firstUserMessage = messages.find(m => m.role === "user");
      const title = firstUserMessage ? generateSessionTitle(firstUserMessage.content) : 'New Chat';
      
      const session: ChatSession = {
        id: currentSessionId,
        title,
        messages: messages.map(msg => ({
          ...msg,
          timestamp: msg.timestamp instanceof Date ? msg.timestamp : new Date(msg.timestamp)
        })),
        lastMessage: messages[messages.length - 1]?.content,
        createdAt: messages[0]?.timestamp instanceof Date ? messages[0].timestamp.toISOString() : new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      saveChatSession(session);
    }
  }, [messages, currentSessionId]);

  const sendMessageToBackend = async (message: string, autoPlayTTS: boolean = false) => {
    try {
      const request: ChatRequest = {
        message,
        session_id: currentSessionId,
      };

      const response = await apiService.chat(request);
      
      // DEBUG: Log the API response
      console.log("🔍 API Response:", response);
      console.log("🔍 Hotel Data:", response.hotel_data);
      console.log("🔍 Hotel Data Length:", response.hotel_data?.length);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.reply || "I'm sorry, I couldn't process your request right now.",
        role: "assistant",
        timestamp: new Date(),
        hotelData: response.hotel_data || undefined,
        selectedHotel: response.selected_hotel || undefined,
        autoPlayTTS: autoPlayTTS,
      };
      
      // DEBUG: Log the message that will be added
      console.log("🔍 Assistant Message:", assistantMessage);
      console.log("🔍 Assistant HotelData:", assistantMessage.hotelData);

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message to backend:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm having trouble connecting to my services right now. Please try again later.",
        role: "assistant",
        timestamp: new Date(),
        autoPlayTTS: autoPlayTTS,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue("");
    setIsLoading(true);

    // Send message to backend
    await sendMessageToBackend(messageToSend);
  };

  const handleVoiceRecording = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      if (audioBlob) {
        try {
          setIsLoading(true);
          
          // Convert audio to text using backend STT
          const transcribedText = await apiService.speechToText(audioBlob);
          
          if (transcribedText.trim()) {
            const userMessage: Message = {
              id: Date.now().toString(),
              content: transcribedText,
              role: "user",
              timestamp: new Date(),
              isVoiceMessage: true,
            };

            setMessages(prev => [...prev, userMessage]);
            
            // Send transcribed message to chat backend with TTS auto-play
            await sendMessageToBackend(transcribedText, true);
          } else {
            // Show error if no text was transcribed
            const errorMessage: Message = {
              id: Date.now().toString(),
              content: "I couldn't understand your voice message. Please try again.",
              role: "assistant",
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
            setIsLoading(false);
          }
        } catch (error) {
          console.error('Voice recording error:', error);
          const errorMessage: Message = {
            id: Date.now().toString(),
            content: "I'm having trouble processing your voice message. Please try again or type your message.",
            role: "assistant",
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
          setIsLoading(false);
        }
      }
    } else {
      await startRecording();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <ChatSidebar isOpen={showSidebar} onClose={() => setShowSidebar(false)} />
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col pb-16 md:pb-0">
        {/* Header */}
        <div className="bg-white border-b px-4 py-3 flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSidebar(true)}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="p-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2 flex-1">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <h1 className="font-semibold text-lg text-primary">Travelry</h1>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // Clear the current session to ensure a new chat is created
              localStorage.removeItem(CURRENT_SESSION_KEY);
              navigate("/chat");
            }}
            className="text-xs"
          >
            <Plus className="w-4 h-4 mr-1" />
            New Chat
          </Button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-12">
              <div className="text-4xl mb-4">✈️</div>
              <p>Tell me about your dream trip and I'll help you find the perfect place to stay!</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div key={message.id}>
              <ChatMessage message={message} />
              {/* Show hotel results if the message has hotel data */}
              {message.role === "assistant" && message.hotelData && message.hotelData.length > 0 && (
                (() => {
                  console.log("🔍 RENDERING HOTEL CARDS:", message.hotelData);
                  
                  // Extract search context from the user's previous message
                  const userMessage = messages[index - 1];
                  const searchText = userMessage?.content?.toLowerCase() || "";
                  
                  // Parse search parameters from user message
                  let city = "Unknown Location";
                  let checkIn = "2025-07-08"; // Default to today
                  let checkOut = "2025-07-10"; // Default to 2 days later
                  let guests = 2;
                  
                  // Extract city
                  const cityMatches = searchText.match(/(?:hotel|in|for)\s+([a-zA-Z\s]+?)(?:\s|$|max|budget|€|\d)/i);
                  if (cityMatches) {
                    city = cityMatches[1].trim().split(' ').map(word => 
                      word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ');
                  } else if (searchText.includes('barcelona')) {
                    city = 'Barcelona';
                  } else if (searchText.includes('madrid')) {
                    city = 'Madrid';
                  } else if (searchText.includes('paris')) {
                    city = 'Paris';
                  }
                  
                  // Extract dates (looking for patterns like "15-17july", "15-17 july", "july 15-17", etc.)
                  const dateMatch = searchText.match(/(\d{1,2})-(\d{1,2})\s*(july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i) ||
                                  searchText.match(/(july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*(\d{1,2})-(\d{1,2})/i);
                  
                  if (dateMatch) {
                    let startDay, endDay, month;
                    
                    // Handle both "15-17july" and "july 15-17" formats
                    if (dateMatch[3]) {
                      // Format: "15-17july"
                      startDay = dateMatch[1];
                      endDay = dateMatch[2];
                      month = dateMatch[3].toLowerCase();
                    } else {
                      // Format: "july 15-17"
                      month = dateMatch[1].toLowerCase();
                      startDay = dateMatch[2];
                      endDay = dateMatch[3];
                    }
                    
                    const year = 2025; // Use 2025 as specified in the logs
                    
                    const monthMap: { [key: string]: string } = {
                      'january': '01', 'jan': '01',
                      'february': '02', 'feb': '02',
                      'march': '03', 'mar': '03',
                      'april': '04', 'apr': '04',
                      'may': '05',
                      'june': '06', 'jun': '06',
                      'july': '07', 'jul': '07',
                      'august': '08', 'aug': '08',
                      'september': '09', 'sep': '09',
                      'october': '10', 'oct': '10',
                      'november': '11', 'nov': '11',
                      'december': '12', 'dec': '12'
                    };
                    
                    const monthNum = monthMap[month] || '07';
                    checkIn = `${year}-${monthNum}-${startDay.padStart(2, '0')}`;
                    checkOut = `${year}-${monthNum}-${endDay.padStart(2, '0')}`;
                  }
                  
                  return (
                    <div className="mt-4 flex justify-start">
                      <div className="bg-white rounded-2xl p-4 max-w-full shadow-sm">
                        <HotelResults 
                          hotels={message.hotelData} 
                          city={city}
                          checkIn={checkIn}
                          checkOut={checkOut}
                          guests={guests}
                        />
                      </div>
                    </div>
                  );
                })()
              )}
              {/* DEBUG: Log all assistant messages to see their data */}
              {message.role === "assistant" && (() => {
                console.log(`🔍 Message ${message.id}: hotelData=${!!message.hotelData}, length=${message.hotelData?.length}`);
                return null;
              })()}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl p-4 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Tell me about your trip..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={handleVoiceRecording}
              disabled={isLoading}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </Button>
            <Button type="submit" disabled={isLoading || !inputValue.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;

// Export the utility functions for use in other components
export { getChatSessions, getChatSession, saveChatSession };
