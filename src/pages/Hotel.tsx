import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Star, MapPin, Wifi, Car, Coffee, Shield } from "lucide-react";
import { apiService } from "@/services/api";

const getAmenityIcon = (iconName: string) => {
  switch (iconName?.toLowerCase()) {
    case 'wifi':
      return Wifi;
    case 'car':
      return Car;
    case 'coffee':
      return Coffee;
    case 'shield':
      return Shield;
    default:
      return Star;
  }
};

const HOTELBEDS_IMAGE_BASE = "https://photos.hotelbeds.com/giata/";

const Hotel = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [hotel, setHotel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImage, setCurrentImage] = useState(0);

  useEffect(() => {
    const fetchHotelDetails = async () => {
      try {
        setLoading(true);
        
        if (!id) {
          throw new Error('Hotel ID is required');
        }

        // Use default dates (next week) to get real prices
        const nextWeek = new Date();
        nextWeek.setDate(nextWeek.getDate() + 7);
        const nextWeekPlusOne = new Date(nextWeek);
        nextWeekPlusOne.setDate(nextWeekPlusOne.getDate() + 1);
        
        const checkIn = nextWeek.toISOString().split('T')[0];
        const checkOut = nextWeekPlusOne.toISOString().split('T')[0];
        
        const data = await apiService.getHotelDetails(id, checkIn, checkOut);
        
        if (!data) {
          throw new Error('Hotel not found');
        }

        setHotel(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching hotel details:', err);
        setError(err.message || 'Failed to load hotel details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchHotelDetails();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading hotel details...</p>
        </div>
      </div>
    );
  }

  if (error || !hotel) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Hotel not found'}</p>
          <Button onClick={() => navigate(-1)} className="mr-2">
            Go Back
          </Button>
          <Button variant="outline" onClick={() => navigate('/chat')}>
            Search Hotels
          </Button>
        </div>
      </div>
    );
  }

  const handleBookNow = () => {
    // Store hotel data in localStorage for payment page
    localStorage.setItem('bookingData', JSON.stringify({
      type: 'hotel',
      id: hotel.id,
      title: hotel.name?.content || hotel.name,
      details: hotel.location,
      date: 'Check-in: Today',
      price: hotel.price,
      currency: hotel.currency || '€',
      originalPrice: hotel.originalPrice,
      rating: hotel.rating,
      image: hotel.images?.[0]
    }));
    navigate(`/pay/${hotel.id}`);
  };

  const handleBackNavigation = () => {
    // Check if there's a stored chat session to return to
    const returnToChatSession = localStorage.getItem('returnToChatSession');
    if (returnToChatSession) {
      // Clear the stored session and navigate back to it
      localStorage.removeItem('returnToChatSession');
      navigate(`/chat/${returnToChatSession}`);
    } else {
      // Default back navigation
      navigate(-1);
    }
  };

  // Helper to get full image URL
  const getImageUrl = (img: string) => {
    if (!img) return "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop";
    if (img.startsWith("http")) return img;
    return `${HOTELBEDS_IMAGE_BASE}${img}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleBackNavigation}
            className="mr-3"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-lg font-semibold truncate">{hotel.name?.content || hotel.name}</h1>
        </div>
      </div>

      {/* Image Carousel */}
      <div className="relative">
        <div className="w-full h-64 overflow-hidden relative">
          <img
            src={getImageUrl(hotel.images?.[currentImage])}
            alt={hotel.name?.content || hotel.name}
            className="w-full h-full object-cover"
          />
          {/* Carousel Controls */}
          {hotel.images && hotel.images.length > 1 && (
            <>
              <button
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/70 rounded-full p-1 shadow"
                onClick={() => setCurrentImage((prev) => (prev === 0 ? hotel.images.length - 1 : prev - 1))}
                aria-label="Previous image"
              >
                &#8592;
              </button>
              <button
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/70 rounded-full p-1 shadow"
                onClick={() => setCurrentImage((prev) => (prev === hotel.images.length - 1 ? 0 : prev + 1))}
                aria-label="Next image"
              >
                &#8594;
              </button>
            </>
          )}
        </div>
        <div className="absolute bottom-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-sm">
          {hotel.images ? currentImage + 1 : 1} / {hotel.images?.length || 1}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6 pb-32">
        {/* Basic Info */}
        <div>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{hotel.name?.content || hotel.name}</h2>
              <div className="flex items-center text-gray-600 mt-1">
                <MapPin className="w-4 h-4 mr-1" />
                <span className="text-sm">{hotel.location}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-baseline">
                <span className="text-2xl font-bold text-primary">{hotel.currency || '€'}{hotel.price}</span>
                {hotel.originalPrice && hotel.originalPrice > hotel.price && (
                  <span className="text-sm text-gray-500 line-through ml-2">{hotel.currency || '€'}{hotel.originalPrice}</span>
                )}
              </div>
              <span className="text-sm text-gray-600">per night</span>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="flex items-center">
              <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
              <span className="font-medium">{hotel.rating}</span>
              <span className="text-gray-600 text-sm ml-1">({hotel.reviews || 0} reviews)</span>
            </div>
            <span className="mx-2 text-gray-400">•</span>
            <span className="text-sm text-gray-600">{hotel.type || hotel.category}</span>
          </div>
        </div>

        {/* Description */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">About this place</h3>
          <p className="text-gray-600 text-sm leading-relaxed">{hotel.description}</p>
        </div>

        {/* Amenities */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Amenities</h3>
          <div className="grid grid-cols-2 gap-3">
            {hotel.amenities && hotel.amenities.length > 0 ? (
              // Handle both string arrays and object arrays
              hotel.amenities.map((amenity, index) => {
                if (typeof amenity === 'string') {
                  // If amenity is a string, create a simple display
                  return (
                    <div key={index} className="flex items-center">
                      <Star className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="text-sm text-gray-700">{amenity}</span>
                    </div>
                  );
                } else if (amenity && typeof amenity === 'object' && amenity.icon && amenity.label) {
                  // If amenity is an object with icon and label
                  const IconComponent = getAmenityIcon(amenity.icon);
                  return (
                    <div key={index} className="flex items-center">
                      <IconComponent className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="text-sm text-gray-700">{amenity.label}</span>
                    </div>
                  );
                }
                return null;
              })
            ) : (
              // Default amenities if none provided
              <>
                <div className="flex items-center">
                  <Wifi className="w-5 h-5 text-gray-600 mr-2" />
                  <span className="text-sm text-gray-700">Free WiFi</span>
                </div>
                <div className="flex items-center">
                  <Coffee className="w-5 h-5 text-gray-600 mr-2" />
                  <span className="text-sm text-gray-700">Restaurant</span>
                </div>
                <div className="flex items-center">
                  <Car className="w-5 h-5 text-gray-600 mr-2" />
                  <span className="text-sm text-gray-700">Parking</span>
                </div>
                <div className="flex items-center">
                  <Shield className="w-5 h-5 text-gray-600 mr-2" />
                  <span className="text-sm text-gray-700">24/7 Security</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Price Breakdown */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mt-8">
          <h3 className="font-semibold text-gray-900 mb-3">Price breakdown</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Room rate</span>
              <span>{hotel.currency || '€'}{hotel.price}</span>
            </div>
            {hotel.originalPrice && hotel.originalPrice > 0 && hotel.originalPrice > hotel.price && (
              <div className="flex justify-between">
                <span className="text-gray-600">Original price</span>
                <span className="text-gray-500 line-through">{hotel.currency || '€'}{hotel.originalPrice}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600">Taxes & fees</span>
              <span>Included</span>
            </div>
            <div className="border-t pt-2 flex justify-between font-semibold">
              <span>Total</span>
              <span>{hotel.currency || '€'}{hotel.price}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Fixed Book Now Button */}
      <div className="fixed bottom-16 left-0 right-0 bg-white border-t border-gray-200 p-4 z-20">
        <Button onClick={handleBookNow} className="w-full">
          Book Now - {hotel.currency || '€'}{hotel.price}
        </Button>
      </div>
    </div>
  );
};

export default Hotel;
