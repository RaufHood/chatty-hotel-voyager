
import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ArrowLeft, Menu, Mic, MicOff } from "lucide-react";
import { ChatMessage } from "@/components/ChatMessage";
import { HotelResults } from "@/components/HotelResults";
import { ChatSidebar } from "@/components/ChatSidebar";
import { useVoiceRecording } from "@/hooks/use-voice-recording";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
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
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'd be happy to help you find the perfect stay! Let me search for the best options based on your request.",
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages([userMessage, assistantMessage]);
      
      // Add default hotel results after a short delay
      setTimeout(() => {
        const hotelResultsMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: "Here are the top recommendations I found for you:",
          role: "assistant",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, hotelResultsMessage]);
      }, 1500);
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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Let me search for the best options for you based on your preferences...",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
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
              {/* Show hotel results after the second assistant message */}
              {message.role === "assistant" && index === 2 && (
                <div className="mt-4 flex justify-start">
                  <div className="bg-white rounded-2xl p-4 max-w-full shadow-sm">
                    <HotelResults />
                  </div>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl p-4 max-w-[85%] shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t bg-white p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Describe your ideal stay..."
              className="flex-1 rounded-full"
              disabled={isRecording}
            />
            <Button 
              type="button"
              size="icon"
              className={`rounded-full ${isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-500 hover:bg-gray-600'}`}
              onClick={handleVoiceRecording}
              disabled={isLoading}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </Button>
            <Button 
              type="submit" 
              size="icon"
              className="rounded-full"
              disabled={!inputValue.trim() || isLoading || isRecording}
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
          {recordingError && (
            <p className="text-red-500 text-sm mt-2">{recordingError}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;
