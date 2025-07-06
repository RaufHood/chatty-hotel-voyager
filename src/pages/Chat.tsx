
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ChatMessage } from "@/components/ChatMessage";
import { HotelRecommendations } from "@/components/HotelRecommendations";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  hotels?: any[];
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hi! I'm your travel assistant. Tell me about your ideal trip - where would you like to go and when?",
      role: "assistant",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const initialMessage = location.state?.initialMessage;
    if (initialMessage) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: initialMessage,
        role: "user",
        timestamp: new Date(),
      };
      setMessages([userMessage]);
      
      // Simulate assistant response
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "I'd be happy to help you find the perfect stay! Let me ask a few quick questions to narrow down the best options for you. What dates are you looking at, and do you have a preferred budget range?",
          role: "assistant",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }, 1000);
    }
  }, [location.state]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

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
        content: "Let me search for the best hotels for you based on your preferences...",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-center">
          <MessageCircle className="w-6 h-6 text-primary mr-2" />
          <h1 className="text-lg font-semibold">TravelChat</h1>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage message={message} />
            {message.hotels && <HotelRecommendations hotels={message.hotels} />}
          </div>
        ))}

        {messages.length >= 4 && (
          <HotelRecommendations hotels={[]} />
        )}

        {isLoading && (
          <div className="chat-bubble chat-bubble-assistant">
            <div className="flex items-center space-x-2">
              <div className="animate-pulse flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
              </div>
              <span className="text-sm text-gray-500">Finding options...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your ideal trip..."
            className="flex-1 rounded-xl border-gray-300 focus:border-primary"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="rounded-xl bg-primary hover:bg-primary/90"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
