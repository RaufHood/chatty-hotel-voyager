from fastapi import APIRouter, Path

router = APIRouter()

@router.get("/pay/{booking_reference}")
async def payment_status(booking_reference: str = Path(..., description="Booking reference code")):
    # TODO: integrate Stripe / provider
    return {"booking_reference": booking_reference, "status": "pending"}
