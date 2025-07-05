
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Star, MapPin, Wifi, Car, Coffee, Shield } from "lucide-react";

const Hotel = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Mock hotel data - in real app this would come from API
  const hotel = {
    id: id,
    name: "The Circus Hostel",
    location: "Mitte, Berlin, Germany",
    price: 28,
    originalPrice: 35,
    rating: 4.5,
    reviews: 1247,
    images: [
      "https://images.unsplash.com/photo-1721322800607-8c38375eef04?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1472396961693-142e6e269027?w=800&h=600&fit=crop"
    ],
    type: "Hostel",
    description: "A vibrant hostel in the heart of Berlin with modern amenities and a great social atmosphere. Perfect for solo travelers and budget-conscious explorers.",
    amenities: [
      { icon: Wifi, label: "Free WiFi" },
      { icon: Coffee, label: "Breakfast" },
      { icon: Car, label: "Parking" },
      { icon: Shield, label: "24/7 Security" }
    ]
  };

  const handleBookNow = () => {
    navigate(`/pay/${hotel.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="mr-3"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-lg font-semibold truncate">{hotel.name}</h1>
        </div>
      </div>

      {/* Image Carousel */}
      <div className="relative">
        <div className="w-full h-64 overflow-hidden">
          <img
            src={hotel.images[0]}
            alt={hotel.name}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="absolute bottom-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-sm">
          1 / {hotel.images.length}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Basic Info */}
        <div>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{hotel.name}</h2>
              <div className="flex items-center text-gray-600 mt-1">
                <MapPin className="w-4 h-4 mr-1" />
                <span className="text-sm">{hotel.location}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-baseline">
                <span className="text-2xl font-bold text-primary">€{hotel.price}</span>
                {hotel.originalPrice > hotel.price && (
                  <span className="text-sm text-gray-500 line-through ml-2">€{hotel.originalPrice}</span>
                )}
              </div>
              <span className="text-sm text-gray-600">per night</span>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="flex items-center">
              <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
              <span className="font-medium">{hotel.rating}</span>
              <span className="text-gray-600 text-sm ml-1">({hotel.reviews} reviews)</span>
            </div>
            <span className="mx-2 text-gray-400">•</span>
            <span className="text-sm text-gray-600">{hotel.type}</span>
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
            {hotel.amenities.map((amenity, index) => (
              <div key={index} className="flex items-center">
                <amenity.icon className="w-5 h-5 text-gray-600 mr-2" />
                <span className="text-sm text-gray-700">{amenity.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Price Breakdown */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Price breakdown</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Room rate</span>
              <span>€{hotel.price}</span>
            </div>
            <div className="flex justify-between">
              <span>Taxes & fees</span>
              <span>€0</span>
            </div>
            <div className="border-t pt-2 font-semibold flex justify-between">
              <span>Total</span>
              <span>€{hotel.price}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="floating-action w-full max-w-md">
        <div className="bg-white border border-gray-200 rounded-2xl p-4 mx-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-bold text-primary">€{hotel.price}</div>
              <div className="text-xs text-gray-500">total price</div>
            </div>
            <Button
              onClick={handleBookNow}
              className="bg-primary hover:bg-primary/90 px-8 py-3 rounded-xl"
            >
              Book Now
            </Button>
          </div>
        </div>
      </div>

      {/* Spacer for floating action */}
      <div className="h-24"></div>
    </div>
  );
};

export default Hotel;
