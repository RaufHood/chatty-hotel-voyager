
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Star, MapPin } from "lucide-react";

interface Hotel {
  id: string;
  name: string;
  location: string;
  price: number;
  rating: number;
  image: string;
  type: string;
}

interface HotelRecommendationsProps {
  hotels: Hotel[];
}

export const HotelRecommendations = ({ hotels }: HotelRecommendationsProps) => {
  const navigate = useNavigate();

  const handleViewHotel = (hotelId: string) => {
    navigate(`/hotel/${hotelId}`);
  };

  return (
    <div className="my-6 space-y-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommended for you</h3>
      <div className="space-y-4">
        {hotels.map((hotel) => (
          <div key={hotel.id} className="hotel-card p-0 overflow-hidden cursor-pointer"
               onClick={() => handleViewHotel(hotel.id)}>
            <div className="flex">
              <div className="w-24 h-20 flex-shrink-0">
                <img
                  src={hotel.image}
                  alt={hotel.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 p-3">
                <div className="flex justify-between items-start mb-1">
                  <h4 className="font-semibold text-gray-900 text-sm leading-tight">{hotel.name}</h4>
                  <div className="text-right ml-2">
                    <div className="text-lg font-bold text-primary">€{hotel.price}</div>
                    <div className="text-xs text-gray-500">per night</div>
                  </div>
                </div>
                <div className="flex items-center text-xs text-gray-600 mb-2">
                  <MapPin className="w-3 h-3 mr-1" />
                  <span>{hotel.location}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Star className="w-3 h-3 text-yellow-400 fill-current mr-1" />
                    <span className="text-xs font-medium">{hotel.rating}</span>
                    <span className="text-xs text-gray-500 ml-1">• {hotel.type}</span>
                  </div>
                  <Button size="sm" variant="outline" className="text-xs px-2 py-1 h-6">
                    View Details
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
