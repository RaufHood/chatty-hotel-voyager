import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ArrowLeft, Menu, Mic, MicOff } from "lucide-react";
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
}

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
  const currentSessionId = sessionId || `session_${Date.now()}`;
  
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

  useEffect(() => {
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
    } else if (!sessionId) {
      // Default welcome message for new chats
      setMessages([
        {
          id: "1",
          content: "Hi! I'm your travel assistant. Tell me about your ideal trip - where would you like to go and when?",
          role: "assistant",
          timestamp: new Date(),
        }
      ]);
    }
  }, [location.state, sessionId]);

  const sendMessageToBackend = async (message: string) => {
    try {
      const request: ChatRequest = {
        message,
        session_id: currentSessionId,
      };

      const response = await apiService.chat(request);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.reply || "I'm sorry, I couldn't process your request right now.",
        role: "assistant",
        timestamp: new Date(),
        hotelData: response.hotel_data || undefined,
        selectedHotel: response.selected_hotel || undefined,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message to backend:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm having trouble connecting to my services right now. Please try again later.",
        role: "assistant",
        timestamp: new Date(),
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
        // For now, simulate converting audio to text
        // Later this will be sent to speech-to-text API
        const userMessage: Message = {
          id: Date.now().toString(),
          content: "[Voice message: Audio recorded successfully - will be processed by speech-to-text]",
          role: "user",
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        // TODO: Send audioBlob to speech-to-text API
        console.log('Audio blob recorded:', audioBlob);

        // Simulate assistant response
        setTimeout(() => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            content: "I heard your voice message! Once we implement speech-to-text, I'll be able to understand and respond to your spoken requests.",
            role: "assistant",
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setIsLoading(false);
        }, 1500);
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
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <h1 className="font-semibold text-lg text-primary">Travelry</h1>
          </div>
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
                <div className="mt-4 flex justify-start">
                  <div className="bg-white rounded-2xl p-4 max-w-full shadow-sm">
                    <HotelResults hotels={message.hotelData} />
                  </div>
                </div>
              )}
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
