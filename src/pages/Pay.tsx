
import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowLeft, CreditCard, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Pay = () => {
  const { ref } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Mock booking data
  const booking = {
    hotelName: "The Circus Hostel",
    location: "Mitte, Berlin",
    checkIn: "Dec 15, 2024",
    checkOut: "Dec 17, 2024",
    nights: 2,
    guests: 1,
    totalPrice: 56
  };

  const handlePayment = async () => {
    setIsProcessing(true);
    
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsProcessing(false);
    setIsSuccess(true);
    
    toast({
      title: "Booking confirmed!",
      description: "You'll receive a confirmation email shortly.",
    });

    // Redirect to trips after success
    setTimeout(() => {
      navigate("/trips");
    }, 2000);
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md mx-auto">
          <div className="mb-6">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Booking Confirmed!</h1>
            <p className="text-gray-600">Your reservation has been successfully processed.</p>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
            <h3 className="font-semibold mb-2">{booking.hotelName}</h3>
            <p className="text-sm text-gray-600 mb-1">{booking.location}</p>
            <p className="text-sm text-gray-600">{booking.checkIn} - {booking.checkOut}</p>
          </div>
          
          <Button onClick={() => navigate("/trips")} className="w-full">
            View My Trips
          </Button>
        </div>
      </div>
    );
  }

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
          <h1 className="text-lg font-semibold">Complete Booking</h1>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Booking Summary */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Booking Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Hotel</span>
              <span className="font-semibold">{booking.hotelName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Location</span>
              <span>{booking.location}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Check-in</span>
              <span>{booking.checkIn}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Check-out</span>
              <span>{booking.checkOut}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Guests</span>
              <span>{booking.guests} guest</span>
            </div>
            <div className="border-t pt-2 flex justify-between font-semibold">
              <span>Total</span>
              <span className="text-primary">€{booking.totalPrice}</span>
            </div>
          </div>
        </div>

        {/* Payment Form */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
            <CreditCard className="w-5 h-5 mr-2" />
            Payment Details
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Card Number
              </label>
              <Input
                placeholder="1234 5678 9012 3456"
                className="w-full"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date
                </label>
                <Input placeholder="MM/YY" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CVV
                </label>
                <Input placeholder="123" />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cardholder Name
              </label>
              <Input placeholder="John Doe" />
            </div>
          </div>
        </div>

        {/* Terms */}
        <div className="text-xs text-gray-500 leading-relaxed">
          By completing this booking, you agree to our Terms of Service and Privacy Policy. 
          Your payment will be processed securely. Free cancellation available until 24 hours before check-in.
        </div>
      </div>

      {/* Bottom Action */}
      <div className="floating-action w-full max-w-md">
        <div className="bg-white border border-gray-200 rounded-2xl p-4 mx-4">
          <Button
            onClick={handlePayment}
            disabled={isProcessing}
            className="w-full bg-primary hover:bg-primary/90 py-3 rounded-xl"
          >
            {isProcessing ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing...
              </div>
            ) : (
              `Confirm & Pay €${booking.totalPrice}`
            )}
          </Button>
        </div>
      </div>

      {/* Spacer for floating action */}
      <div className="h-24"></div>
    </div>
  );
};

export default Pay;
