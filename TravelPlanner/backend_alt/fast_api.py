#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 17:16:42 2025

@author: aleksei
"""
#
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from io import BytesIO
import os

#os.chdir("/home/aleksei/Documents/GitHub/chatty-hotel-voyager/TravelPlanner/backend_alt/")
#local import
from llm_tts_stt import call_groq, stt, tts

app = FastAPI()

class TTSPayload(BaseModel):
    text: str
    
    
class LLMPayload(BaseModel):
    system_prompt: str
    message: str
    history: list

@app.post("/tts")
async def text_to_speech(payload: TTSPayload):
    try:
        text = payload.dict()['text']
        output = tts(text)
        buffer = BytesIO(output)
        return StreamingResponse(buffer, media_type="application/octet-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
        
@app.post("/stt")
async def speect_to_text(payload: UploadFile = File(...)):
    try:
        audio = await payload.read()
        output = stt(audio)
        return {"voice": output}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat")
async def chat(payload: LLMPayload):
    try:
        system_prompt = payload.dict()['system_prompt']
        message = payload.dict()['message']
        history = payload.dict()['history'] #must be a list of dictionaries        
        out = call_groq(system_prompt, message, history)
        
        history.append({"role": "assistant", "content": out})            
        
        return {"message": "OK", "response": out, "history": history}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",
                     port=8000)
