from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_trips():
    # TODO: List trips from DB
    return []
