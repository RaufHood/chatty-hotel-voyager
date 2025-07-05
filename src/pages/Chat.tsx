
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, MessageCircle } from "lucide-react";
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
    scrollToBottom();
  }, [messages]);

  const simulateAssistantResponse = async (userMessage: string) => {
    setIsLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    let response = "";
    let hotels = null;

    // Simple keyword-based responses for demo
    if (userMessage.toLowerCase().includes("berlin") || userMessage.toLowerCase().includes("germany")) {
      response = "Great choice! Berlin has amazing options. Based on your preferences, here are some perfect matches:";
      hotels = [
        {
          id: "1",
          name: "The Circus Hostel",
          location: "Mitte, Berlin",
          price: 28,
          rating: 4.5,
          image: "https://images.unsplash.com/photo-1721322800607-8c38375eef04?w=400&h=300&fit=crop",
          type: "Hostel"
        },
        {
          id: "2",
          name: "Hotel Adlon Kempinski",
          location: "Brandenburg Gate, Berlin",
          price: 450,
          rating: 4.8,
          image: "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?w=400&h=300&fit=crop",
          type: "Luxury Hotel"
        },
        {
          id: "3",
          name: "Meininger Hotel Berlin",
          location: "Alexanderplatz, Berlin",
          price: 89,
          rating: 4.2,
          image: "https://images.unsplash.com/photo-1472396961693-142e6e269027?w=400&h=300&fit=crop",
          type: "Hotel"
        }
      ];
    } else if (userMessage.toLowerCase().includes("budget") || userMessage.toLowerCase().includes("cheap")) {
      response = "I understand you're looking for budget-friendly options. What's your ideal price range per night, and which city are you considering?";
    } else if (userMessage.toLowerCase().includes("luxury") || userMessage.toLowerCase().includes("expensive")) {
      response = "Looking for a premium experience! What destination did you have in mind? I can find the finest hotels with top-notch amenities.";
    } else if (userMessage.toLowerCase().includes("weekend") || userMessage.toLowerCase().includes("dates")) {
      response = "Perfect! Could you share your specific dates and which city you'd like to visit? This helps me find the best availability and prices.";
    } else {
      response = "That sounds interesting! Could you tell me a bit more about your destination, dates, and what kind of accommodation you prefer? (hotel, hostel, budget range)";
    }

    const assistantMessage: Message = {
      id: Date.now().toString(),
      content: response,
      role: "assistant",
      timestamp: new Date(),
      hotels
    };

    setMessages(prev => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput("");

    await simulateAssistantResponse(currentInput);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
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
