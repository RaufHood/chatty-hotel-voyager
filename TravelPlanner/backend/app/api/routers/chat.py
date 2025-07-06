from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def chat(prompt: str):
    # TODO: integrate LangChain agent
    return {"reply": f"Echo: {prompt}"}
