
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Plane, Clock, Calendar, MapPin, Users } from 'lucide-react';

const Flight = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Mock flight data - in real app, fetch by ID
  const flight = {
    id: id,
    airline: "Air France",
    flightNumber: "AF 1234",
    aircraft: "Airbus A320",
    departureAirport: "Charles de Gaulle (CDG)",
    arrivalAirport: "London Heathrow (LHR)",
    departureCity: "Paris",
    arrivalCity: "London",
    departureTime: "14:30",
    arrivalTime: "15:45",
    date: "July 15, 2024",
    duration: "1h 15m",
    price: 156,
    class: "Economy",
    baggage: "1 carry-on, 1 checked bag",
    seats: "12A, 12B",
    bookingReference: "AF123XYZ",
    status: "Confirmed"
  };

  const handleBookFlight = () => {
    navigate(`/pay/flight-${flight.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2">
            <Plane className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Flight Details</h1>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Flight Overview Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Plane className="w-5 h-5" />
                {flight.airline} {flight.flightNumber}
              </CardTitle>
              <Badge variant={flight.status === 'Confirmed' ? 'default' : 'secondary'}>
                {flight.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Route */}
            <div className="flex items-center justify-between">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{flight.departureTime}</div>
                <div className="text-sm text-gray-600">{flight.departureCity}</div>
                <div className="text-xs text-gray-500">{flight.departureAirport}</div>
              </div>
              
              <div className="flex-1 mx-6 relative">
                <div className="border-t-2 border-dashed border-gray-300"></div>
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="bg-white p-1">
                    <Plane className="w-4 h-4 text-primary rotate-90" />
                  </div>
                </div>
                <div className="text-center mt-2">
                  <span className="text-xs text-gray-500">{flight.duration}</span>
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{flight.arrivalTime}</div>
                <div className="text-sm text-gray-600">{flight.arrivalCity}</div>
                <div className="text-xs text-gray-500">{flight.arrivalAirport}</div>
              </div>
            </div>

            {/* Flight Info */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium">Date</div>
                  <div className="text-xs text-gray-600">{flight.date}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Plane className="w-4 h-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium">Aircraft</div>
                  <div className="text-xs text-gray-600">{flight.aircraft}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium">Class</div>
                  <div className="text-xs text-gray-600">{flight.class}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium">Seats</div>
                  <div className="text-xs text-gray-600">{flight.seats}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Booking Details */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Booking Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Booking Reference</span>
              <span className="font-mono font-medium">{flight.bookingReference}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Baggage</span>
              <span>{flight.baggage}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status</span>
              <Badge variant="outline">{flight.status}</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Price and Actions */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-gray-600">Total Price</div>
                <div className="text-2xl font-bold text-primary">€{flight.price}</div>
                <div className="text-xs text-gray-500">per person</div>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button onClick={handleBookFlight} className="flex-1">
                Book This Flight
              </Button>
              <Button variant="outline" onClick={() => navigate('/chat')}>
                Find Similar
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Flight;
