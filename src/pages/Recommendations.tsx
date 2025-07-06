import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Heart, Phone, MapPin, Star } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { HotelRecommendations } from '@/components/HotelRecommendations';

interface UserProfile {
  id: string;
  phone_number?: string;
}

const Recommendations = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [hasPhoneNumber, setHasPhoneNumber] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Mock hotel recommendations data (similar to what's shown in chat)
  const recommendedHotels = [
    {
      id: "1",
      name: "Le Meurice",
      location: "1st Arrondissement, Paris",
      price: 850,
      rating: 4.8,
      image: "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400&h=300&fit=crop",
      type: "Luxury Hotel"
    },
    {
      id: "2", 
      name: "Hotel des Grands Boulevards",
      location: "2nd Arrondissement, Paris",
      price: 220,
      rating: 4.5,
      image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop",
      type: "Boutique Hotel"
    },
    {
      id: "3",
      name: "Generator Paris",
      location: "10th Arrondissement, Paris", 
      price: 65,
      rating: 4.2,
      image: "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=400&h=300&fit=crop",
      type: "Modern Hostel"
    }
  ];

  useEffect(() => {
    if (user) {
      checkUserProfile();
    }
  }, [user]);

  const checkUserProfile = async () => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('id, phone_number')
        .eq('id', user?.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        // PGRST116 is "not found" error, which is expected for new users
        console.error('Error fetching profile:', error);
        toast({
          title: 'Error',
          description: 'Failed to load profile information.',
          variant: 'destructive'
        });
        return;
      }

      if (data?.phone_number) {
        setHasPhoneNumber(true);
        setPhoneNumber(data.phone_number);
      }
    } catch (error) {
      console.error('Error checking profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumber.trim()) return;

    setSubmitting(true);
    
    try {
      // First, try to update existing profile
      const { error: updateError } = await supabase
        .from('profiles')
        .update({ phone_number: phoneNumber })
        .eq('id', user?.id);

      if (updateError) {
        // If update fails, try to insert new profile
        const { error: insertError } = await supabase
          .from('profiles')
          .insert([
            {
              id: user?.id,
              phone_number: phoneNumber,
              email: user?.email
            }
          ]);

        if (insertError) {
          throw insertError;
        }
      }

      setHasPhoneNumber(true);
      toast({
        title: 'Phone number saved!',
        description: 'Your phone number has been saved successfully.'
      });
    } catch (error) {
      console.error('Error saving phone number:', error);
      toast({
        title: 'Error',
        description: 'Failed to save phone number. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-16 md:pb-0">
      {/* Header */}
      <div className="bg-white border-b px-4 py-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="h-8 w-8"
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Heart className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-xl font-semibold">Recommendations</h1>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {!hasPhoneNumber ? (
          /* Phone Number Collection */
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="w-5 h-5" />
                Complete Your Profile
              </CardTitle>
              <CardDescription>
                We need your phone number to send you personalized hotel recommendations and booking updates.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePhoneSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+33 1 23 45 67 89"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                  />
                  <p className="text-sm text-gray-600">
                    We'll use this to send you booking confirmations and special offers.
                  </p>
                </div>
                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={submitting || !phoneNumber.trim()}
                >
                  {submitting ? 'Saving...' : 'Save Phone Number'}
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          /* Hotel Recommendations */
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Recommended for You
              </h2>
              <p className="text-gray-600">
                Based on your preferences, here are our top hotel picks in Paris
              </p>
            </div>

            {/* Featured Recommendations */}
            <div className="space-y-4">
              {recommendedHotels.map((hotel) => (
                <Card key={hotel.id} className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => navigate(`/hotel/${hotel.id}`)}>
                  <CardContent className="p-0">
                    <div className="flex">
                      <div className="w-32 h-24 flex-shrink-0">
                        <img
                          src={hotel.image}
                          alt={hotel.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-gray-900">{hotel.name}</h3>
                          <div className="text-right">
                            <div className="text-lg font-bold text-primary">€{hotel.price}</div>
                            <div className="text-xs text-gray-500">per night</div>
                          </div>
                        </div>
                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <MapPin className="w-4 h-4 mr-1" />
                          <span>{hotel.location}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                            <span className="text-sm font-medium">{hotel.rating}</span>
                            <span className="text-sm text-gray-500 ml-2">• {hotel.type}</span>
                          </div>
                          <Button size="sm" variant="outline" className="ml-2">
                            View Details
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Call to Action */}
            <Card className="mt-6">
              <CardContent className="p-6 text-center">
                <Heart className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Want More Recommendations?</h3>
                <p className="text-gray-600 mb-4">
                  Chat with our AI assistant to get personalized hotel suggestions for any destination.
                </p>
                <Button onClick={() => navigate('/chat')} className="w-full">
                  Start Chatting
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations; 