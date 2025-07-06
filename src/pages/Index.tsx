
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { MessageCircle, Star, Clock, Shield, Search, User } from "lucide-react";

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
    // TODO: Implement login logic with backend
    console.log("Login submitted");
    setIsLoginOpen(false);
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement signup logic with backend
    console.log("Signup submitted");
    setIsSignupOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-orange-50">
      {/* Header with Auth */}
      <div className="container mx-auto px-4 pt-6">
        <div className="flex justify-end gap-2">
          <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm">
                <User className="w-4 h-4 mr-2" />
                Login
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Login to TravelChat</DialogTitle>
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
                <DialogTitle>Join TravelChat</DialogTitle>
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
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-16 pb-8">
        <div className="text-center max-w-3xl mx-auto">
          <div className="mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-6">
              <MessageCircle className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Find Your Perfect Stay
            </h1>
            <p className="text-xl text-gray-600 mb-12">
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
