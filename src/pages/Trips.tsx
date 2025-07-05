
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Calendar, MapPin, Star, MessageCircle } from "lucide-react";

const Trips = () => {
  const navigate = useNavigate();

  // Mock trips data
  const trips = [
    {
      id: "1",
      hotelName: "The Circus Hostel",
      location: "Berlin, Germany",
      checkIn: "Dec 15, 2024",
      checkOut: "Dec 17, 2024",
      status: "Confirmed",
      price: 56,
      image: "https://images.unsplash.com/photo-1721322800607-8c38375eef04?w=400&h=300&fit=crop"
    }
  ];

  const watchedSearches = [
    {
      id: "1",
      query: "Budget hostels in Amsterdam",
      createdAt: "2 days ago",
      priceAlert: true
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(-1)}
              className="mr-3"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-lg font-semibold">My Trips</h1>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate("/chat")}
          >
            <MessageCircle className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Upcoming Trips */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Trips</h2>
          {trips.length > 0 ? (
            <div className="space-y-3">
              {trips.map((trip) => (
                <div key={trip.id} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex">
                    <div className="w-16 h-12 flex-shrink-0 rounded-lg overflow-hidden">
                      <img
                        src={trip.image}
                        alt={trip.hotelName}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1 ml-3">
                      <div className="flex justify-between items-start mb-1">
                        <h3 className="font-semibold text-gray-900 text-sm">{trip.hotelName}</h3>
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                          {trip.status}
                        </span>
                      </div>
                      <div className="flex items-center text-xs text-gray-600 mb-2">
                        <MapPin className="w-3 h-3 mr-1" />
                        <span>{trip.location}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center text-xs text-gray-600">
                          <Calendar className="w-3 h-3 mr-1" />
                          <span>{trip.checkIn} - {trip.checkOut}</span>
                        </div>
                        <span className="text-sm font-semibold text-primary">€{trip.price}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No upcoming trips</p>
              <Button
                variant="outline"
                className="mt-3"
                onClick={() => navigate("/chat")}
              >
                Plan a Trip
              </Button>
            </div>
          )}
        </div>

        {/* Watched Searches */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Price Alerts</h2>
          {watchedSearches.length > 0 ? (
            <div className="space-y-3">
              {watchedSearches.map((search) => (
                <div key={search.id} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{search.query}</h3>
                      <p className="text-sm text-gray-600 mt-1">Created {search.createdAt}</p>
                    </div>
                    <div className="flex items-center">
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                        Watching
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Star className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No price alerts set</p>
              <p className="text-sm text-gray-400 mt-1">
                Ask our assistant to watch prices for your searches
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Trips;
