
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MapPin, Star, Wifi, Car, Coffee, Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Hotel {
  id: string;
  name: string;
  location: string;
  rating: number;
  price: number;
  originalPrice?: number;
  image: string;
  amenities: string[];
  description: string;
}

interface HotelResultsProps {
  hotels?: Hotel[];
  title?: string;
  city?: string;
  checkIn?: string;
  checkOut?: string;
  guests?: number;
}

export const HotelResults: React.FC<HotelResultsProps> = ({ 
  hotels, 
  title,
  city = "Paris",
  checkIn = "2024-07-08",
  checkOut = "2024-07-09", 
  guests = 2
}) => {
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  // Mock data for Paris hotels
  const defaultHotels: Hotel[] = [
    {
      id: "1",
      name: "Hotel des Grands Boulevards",
      location: "2nd Arrondissement, Paris",
      rating: 4.5,
      price: 156,
      originalPrice: 180,
      image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop",
      amenities: ["Free WiFi", "Restaurant", "Bar"],
      description: "Stylish boutique hotel in the heart of Paris with modern amenities."
    },
    {
      id: "2", 
      name: "Le Marais Boutique Hotel",
      location: "4th Arrondissement, Paris",
      rating: 4.3,
      price: 134,
      originalPrice: 155,
      image: "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400&h=300&fit=crop",
      amenities: ["Free WiFi", "Parking", "Breakfast"],
      description: "Charming hotel in the historic Marais district with traditional French charm."
    },
    {
      id: "3",
      name: "Montmartre View Hotel",
      location: "18th Arrondissement, Paris", 
      rating: 4.7,
      price: 189,
      image: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400&h=300&fit=crop",
      amenities: ["Free WiFi", "City View", "Concierge"],
      description: "Elegant hotel with stunning views of Sacré-Cœur and Paris skyline."
    }
  ];

  const displayHotels = hotels || defaultHotels;

  // Generate dynamic title if not provided
  const finalTitle = title || `Top 3 Hotels for ${city}`;
  
  // Calculate nights and format dates
  const calculateNights = (checkIn: string, checkOut: string) => {
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    const diffTime = checkOutDate.getTime() - checkInDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };
  
  const nights = calculateNights(checkIn, checkOut);
  const dateInfo = `${formatDate(checkIn)}-${formatDate(checkOut)}, ${new Date(checkIn).getFullYear()} • ${nights} night${nights !== 1 ? 's' : ''} • ${guests} guest${guests !== 1 ? 's' : ''}`;

  const toggleFavorite = (hotelId: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(hotelId)) {
        newFavorites.delete(hotelId);
      } else {
        newFavorites.add(hotelId);
      }
      return newFavorites;
    });
  };

  const getAmenityIcon = (amenity: string) => {
    if (amenity.toLowerCase().includes('wifi')) return <Wifi className="w-3 h-3" />;
    if (amenity.toLowerCase().includes('parking') || amenity.toLowerCase().includes('car')) return <Car className="w-3 h-3" />;
    if (amenity.toLowerCase().includes('breakfast') || amenity.toLowerCase().includes('restaurant')) return <Coffee className="w-3 h-3" />;
    return <Star className="w-3 h-3" />;
  };

  return (
    <div className="w-full max-w-2xl">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{finalTitle}</h3>
        <p className="text-sm text-gray-600">{dateInfo}</p>
      </div>
      
      <div className="space-y-4">
        {displayHotels.map((hotel) => (
          <Card key={hotel.id} className="overflow-hidden hover:shadow-md transition-shadow">
            <CardContent className="p-0">
              <div className="flex">
                {/* Hotel Image */}
                <div className="w-32 h-24 flex-shrink-0">
                  <img
                    src={hotel.image}
                    alt={hotel.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                
                {/* Hotel Details */}
                <div className="flex-1 p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm text-gray-900 mb-1">
                        {hotel.name}
                      </h4>
                      <div className="flex items-center text-xs text-gray-600 mb-1">
                        <MapPin className="w-3 h-3 mr-1" />
                        <span>{hotel.location}</span>
                      </div>
                      <div className="flex items-center mb-2">
                        <div className="flex items-center">
                          <Star className="w-3 h-3 text-yellow-400 fill-current" />
                          <span className="text-xs font-medium ml-1">{hotel.rating}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Price */}
                    <div className="text-right ml-4">
                      <div className="flex items-center gap-1">
                        {hotel.originalPrice && (
                          <span className="text-xs text-gray-500 line-through">
                            €{hotel.originalPrice}
                          </span>
                        )}
                        <span className="text-sm font-bold text-gray-900">
                          €{hotel.price}
                        </span>
                      </div>
                      <span className="text-xs text-gray-600">per night</span>
                    </div>
                  </div>
                  
                  {/* Amenities */}
                  <div className="flex flex-wrap gap-1 mb-2">
                    {hotel.amenities.slice(0, 3).map((amenity, index) => (
                      <Badge key={index} variant="secondary" className="text-xs px-2 py-1">
                        <span className="mr-1">{getAmenityIcon(amenity)}</span>
                        {amenity}
                      </Badge>
                    ))}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center justify-between mt-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/hotel/${hotel.id}`)}
                    >
                      View Details
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleFavorite(hotel.id)}
                      className="p-2"
                    >
                      <Heart 
                        className={`w-4 h-4 ${
                          favorites.has(hotel.id) 
                            ? 'text-red-500 fill-current' 
                            : 'text-gray-400'
                        }`} 
                      />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <Button variant="outline" onClick={() => navigate('/chat')}>
          View All Results
        </Button>
      </div>
    </div>
  );
};
