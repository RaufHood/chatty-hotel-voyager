
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft, CreditCard, Lock, Hotel, Plane } from 'lucide-react';
import { useState } from 'react';

const Pay = () => {
  const { ref } = useParams();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);

  // Determine if it's a flight or hotel booking
  const isFlightBooking = ref?.startsWith('flight-');
  const bookingType = isFlightBooking ? 'flight' : 'hotel';
  const bookingId = ref?.replace('flight-', '').replace('hotel-', '') || ref;

  // Mock booking data
  const bookingData = isFlightBooking ? {
    type: 'Flight',
    title: 'Air France AF 1234',
    details: 'Paris CDG → London LHR',
    date: 'July 15, 2024',
    price: 156,
    icon: Plane
  } : {
    type: 'Hotel',
    title: 'The Circus Hostel',
    details: 'Berlin, Germany',
    date: 'Dec 15-17, 2024',
    price: 112,
    icon: Hotel
  };

  const handlePayment = async () => {
    setProcessing(true);
    
    // Simulate payment processing
    setTimeout(() => {
      setProcessing(false);
      // Navigate to success page or trips
      navigate('/trips', { 
        state: { 
          message: `Your ${bookingData.type.toLowerCase()} has been booked successfully!` 
        }
      });
    }, 2000);
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
            <CreditCard className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Complete Payment</h1>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Booking Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <bookingData.icon className="w-5 h-5" />
              {bookingData.type} Booking Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="font-medium">{bookingData.title}</span>
                <span className="text-sm text-gray-600">{bookingData.details}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Date</span>
                <span>{bookingData.date}</span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t">
                <span className="font-semibold">Total</span>
                <span className="text-xl font-bold text-primary">€{bookingData.price}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Payment Form */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="w-5 h-5" />
              Payment Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cardNumber">Card Number</Label>
              <Input
                id="cardNumber"
                placeholder="1234 5678 9012 3456"
                className="font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="expiry">Expiry Date</Label>
                <Input
                  id="expiry"
                  placeholder="MM/YY"
                  className="font-mono"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cvv">CVV</Label>
                <Input
                  id="cvv"
                  placeholder="123"
                  className="font-mono"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cardName">Cardholder Name</Label>
              <Input
                id="cardName"
                placeholder="John Doe"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="john@example.com"
              />
            </div>

            <div className="pt-4">
              <Button
                onClick={handlePayment}
                disabled={processing}
                className="w-full"
                size="lg"
              >
                {processing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4 mr-2" />
                    Pay €{bookingData.price}
                  </>
                )}
              </Button>
            </div>

            <div className="text-center text-sm text-gray-500 pt-2">
              <Lock className="w-4 h-4 inline mr-1" />
              Your payment is secured with 256-bit SSL encryption
            </div>
          </CardContent>
        </Card>

        {/* Security Notice */}
        <div className="text-center text-sm text-gray-600">
          <p>By completing this purchase you agree to our terms and conditions.</p>
          <p className="mt-1">You will receive a confirmation email after payment.</p>
        </div>
      </div>
    </div>
  );
};

export default Pay;
