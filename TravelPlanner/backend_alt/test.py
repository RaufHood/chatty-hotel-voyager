#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 21:08:32 2025

@author: aleksei
"""
import requests

path = "/home/aleksei/"

#tts
out = requests.post("http://127.0.0.1:8000/tts",
              json={"text": "Hello, how is it going?"})

#stt
with open(path + 'test.mp3', 'rb') as f:
    files = {'payload': ('test.mp3', f, 'audio/mp3')}
    response = requests.post('http://127.0.0.1:8000/stt', files=files)

print(response.status_code)
print(response.json())

#llm:
system_prompt = "You are a great scientist"
conv_history =  [
		{
		    "role": "user",
		    "content": "Hello"
		},
		
		{
		    "role": "assistant",
		    "content": "Hello, how can I help you?"
		}
        
    ]

message = "Tell me about Llama language models"

out = requests.post("http://127.0.0.1:8000/chat",
                    json = {
                            "system_prompt": system_prompt,
                            "message": message,
                            "history": conv_history
                            })
print(out.status_code)
print(out.json())
