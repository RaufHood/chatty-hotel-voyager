import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageCircle, Star, Clock, Shield, Search, User, MapPin, Plane, Send, Mic, MicOff } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useVoiceRecording } from "@/hooks/use-voice-recording";

const Index = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  
  const { 
    isRecording, 
    startRecording, 
    stopRecording, 
    error: recordingError 
  } = useVoiceRecording();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      if (user) {
        navigate("/chat", { state: { initialMessage: searchQuery } });
      } else {
        navigate("/auth");
      }
    }
  };

  const handleVoiceRecording = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      if (audioBlob) {
        // For now, simulate converting audio to text
        // When voice recording is released, send the message
        const voiceMessage = "[Voice message recorded - will be processed by speech-to-text]";
        
        if (user) {
          navigate("/chat", { state: { initialMessage: voiceMessage } });
        } else {
          navigate("/auth");
        }
        
        // TODO: Send audioBlob to speech-to-text API
        console.log('Audio blob recorded on index page:', audioBlob);
      }
    } else {
      await startRecording();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-orange-50">
      {/* Header with Logo and Auth */}
      <div className="container mx-auto px-4 pt-6">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-sm">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <h1 className="text-2xl font-bold text-primary">Travelry</h1>
          </div>

          {/* Auth Buttons */}
          <div className="flex gap-2">
            {user ? (
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/trips")}
                >
                  My Trips
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/chat")}
                >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Chat
                </Button>
              </div>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/auth")}
                >
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/auth")}
                >
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-12 pb-8">
        <div className="text-center max-w-2xl mx-auto">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-6">
              <MessageCircle className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Hotel booking in seconds
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Skip the endless scrolling. Just tell us what you need and we'll find the best hotels at transparent prices.
            </p>
          </div>
          
          {/* Chat-style search input */}
          <form onSubmit={handleSearch} className="mb-8">
            <div className="relative max-w-2xl mx-auto">
              <div className="relative bg-white rounded-2xl shadow-lg border border-gray-200 p-1">
                <div className="flex items-center px-4 py-3 gap-3">
                  <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="I need a hotel in Paris for next weekend..."
                    className="border-0 bg-transparent text-lg placeholder:text-gray-500 focus-visible:ring-0 flex-1"
                    disabled={isRecording}
                  />
                  <Button 
                    type="button"
                    size="icon"
                    className={`rounded-full ${isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-500 hover:bg-gray-600'}`}
                    onClick={handleVoiceRecording}
                  >
                    {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </Button>
                  <Button 
                    type="submit"
                    size="icon"
                    className="rounded-full bg-primary hover:bg-primary/90"
                    disabled={!searchQuery.trim() || isRecording}
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              {recordingError && (
                <p className="text-red-500 text-sm mt-2 text-center">{recordingError}</p>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* Destinations Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Discover Amazing Destinations
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            From vibrant cities to cultural gems, find your perfect stay in the world's most exciting destinations
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Barcelona */}
          <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="relative h-80">
              <img 
                src="/barcelona.webp" 
                alt="Barcelona, Spain" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                <div className="flex items-center mb-2">
                  <MapPin className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">Barcelona, Spain</span>
                </div>
                <h3 className="text-2xl font-bold mb-2">Barcelona</h3>
                <p className="text-sm text-gray-200 mb-4">
                  Experience the magic of Gaudí's architecture, vibrant street life, and Mediterranean charm
                </p>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => {
                    const message = "I want to find hotels in Barcelona";
                    if (user) {
                      navigate("/chat", { state: { initialMessage: message } });
                    } else {
                      navigate("/auth");
                    }
                  }}
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm border-white/30"
                >
                  <Plane className="w-4 h-4 mr-2" />
                  Find Hotels
                </Button>
              </div>
            </div>
          </div>

          {/* London */}
          <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="relative h-80">
              <img 
                src="/london.jpg" 
                alt="London, UK" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                <div className="flex items-center mb-2">
                  <MapPin className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">London, UK</span>
                </div>
                <h3 className="text-2xl font-bold mb-2">London</h3>
                <p className="text-sm text-gray-200 mb-4">
                  Discover historic landmarks, world-class museums, and the perfect blend of tradition and innovation
                </p>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => {
                    const message = "I want to find hotels in London";
                    if (user) {
                      navigate("/chat", { state: { initialMessage: message } });
                    } else {
                      navigate("/auth");
                    }
                  }}
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm border-white/30"
                >
                  <Plane className="w-4 h-4 mr-2" />
                  Find Hotels
                </Button>
              </div>
            </div>
          </div>

          {/* Singapore */}
          <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
            <div className="relative h-80">
              <img 
                src="/singapore.webp" 
                alt="Singapore" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                <div className="flex items-center mb-2">
                  <MapPin className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">Singapore</span>
                </div>
                <h3 className="text-2xl font-bold mb-2">Singapore</h3>
                <p className="text-sm text-gray-200 mb-4">
                  Explore futuristic architecture, diverse cultures, and the perfect fusion of nature and urban life
                </p>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => {
                    const message = "I want to find hotels in Singapore";
                    if (user) {
                      navigate("/chat", { state: { initialMessage: message } });
                    } else {
                      navigate("/auth");
                    }
                  }}
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm border-white/30"
                >
                  <Plane className="w-4 h-4 mr-2" />
                  Find Hotels
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">Ready to explore more destinations?</p>
          <Button 
            onClick={() => user ? navigate("/chat") : navigate("/auth")}
            className="bg-primary hover:bg-primary/90 text-white px-8 py-3 rounded-xl text-lg"
          >
            <Search className="w-5 h-5 mr-2" />
            Start Your Journey
          </Button>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-orange-100 rounded-xl mb-4">
              <MessageCircle className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Natural Conversation</h3>
            <p className="text-gray-600">Just describe your trip in your own words. No complex forms or filters.</p>
          </div>
          
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-xl mb-4">
              <Shield className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Transparent Pricing</h3>
            <p className="text-gray-600">See the total price upfront. No hidden fees or surprises at checkout.</p>
          </div>
          
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-xl mb-4">
              <Clock className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Quick Booking</h3>
            <p className="text-gray-600">From search to booked in minutes. One-tap confirmation for your perfect stay.</p>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-sm p-8 max-w-2xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
            ))}
          </div>
          <p className="text-gray-600 mb-4 italic">
            "Finally, a travel app that actually understands what I'm looking for. Found the perfect hostel in Berlin in under 2 minutes!"
          </p>
          <p className="text-sm text-gray-500">- Sophie, Backpacker from Germany</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
