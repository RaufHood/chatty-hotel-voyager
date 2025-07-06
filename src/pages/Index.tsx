import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { MessageCircle, Star, Clock, Shield, Search, User, MapPin, Plane } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate("/chat", { state: { initialMessage: searchQuery } });
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement OAuth login with backend
    console.log("Login submitted");
    setIsLoginOpen(false);
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement OAuth signup with backend
    console.log("Signup submitted");
    setIsSignupOpen(false);
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
            <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
              <DialogTrigger asChild>
                <Button variant="ghost" size="sm">
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Login to Travelry</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input id="login-email" type="email" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <Input id="login-password" type="password" required />
                  </div>
                  <Button type="submit" className="w-full">
                    Login
                  </Button>
                  <div className="text-center text-sm text-gray-500">
                    OAuth integration coming soon
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog open={isSignupOpen} onOpenChange={setIsSignupOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  Sign Up
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Join Travelry</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="signup-firstname">First Name</Label>
                      <Input id="signup-firstname" required />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-lastname">Last Name</Label>
                      <Input id="signup-lastname" required />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <Input id="signup-email" type="email" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <Input id="signup-password" type="password" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password-confirm">Confirm Password</Label>
                    <Input id="signup-password-confirm" type="password" required />
                  </div>
                  <Button type="submit" className="w-full">
                    Create Account
                  </Button>
                  <div className="text-center text-sm text-gray-500">
                    OAuth integration coming soon
                  </div>
                </form>
              </DialogContent>
            </Dialog>
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
          
          {/* Perplexity-style search input */}
          <form onSubmit={handleSearch} className="mb-8">
            <div className="relative max-w-2xl mx-auto">
              <div className="relative bg-white rounded-2xl shadow-lg border border-gray-200 p-1">
                <div className="flex items-center px-4 py-3">
                  <Search className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="I need a hotel in Paris for next weekend..."
                    className="border-0 bg-transparent text-lg placeholder:text-gray-500 focus-visible:ring-0 flex-1"
                  />
                  <Button 
                    type="submit"
                    className="ml-2 bg-primary hover:bg-primary/90 text-white px-6 py-2 rounded-xl"
                    disabled={!searchQuery.trim()}
                  >
                    Search
                  </Button>
                </div>
              </div>
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
                  onClick={() => navigate("/chat", { state: { initialMessage: "I want to find hotels in Barcelona" } })}
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
                  onClick={() => navigate("/chat", { state: { initialMessage: "I want to find hotels in London" } })}
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
                  onClick={() => navigate("/chat", { state: { initialMessage: "I want to find hotels in Singapore" } })}
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
            onClick={() => navigate("/chat")}
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
