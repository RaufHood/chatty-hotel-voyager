import os
from groq import Groq
import uuid
from elevenlabs import ElevenLabs
from tempfile import NamedTemporaryFile

GROQ_API_KEY = os.environ('GROQ_API_KEY')
ELEVENLABS_API_KEY = os.environ('ELEVENLABS_API_KEY')

PATH = "/home/aleksei/" #replace with actual path once we deploy backend on a VM

def call_groq(system_prompt: str,
              user_message: str,
		      conv_history: list) -> str:
    """
    conv_history needs to be a list of dictionaries of the format:
    
    [
		{
		    "role": "user",
		    "content": "Hello"
		},
		
		{
		    "role": "assistant",
		    "content": "Hello, how can I help you?"
		},
    [
    """
    
    client = Groq(api_key = GROQ_API_KEY)
    
    messages=[
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    for message in conv_history:
    	messages.append(message)
    
    #add the latest user message last:
    messages.append({"role": "user", "content": user_message})
    
    print(messages)
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )
    output = chat_completion.choices[0].message.content
    
    return output
    
def stt(audio_bytes: bytes) -> str:
    
    client = Groq(api_key=GROQ_API_KEY)
    
    with NamedTemporaryFile(suffix = ".mp3", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3",
                language="en"
            )
    print(transcription)
    return transcription.text

def tts(text: str) -> bytes:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    output = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_multilingual_v2"
    )
    audio_bytes = b"".join(output)
    return audio_bytes
    
    
#tests
"""
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
out = call_groq(system_prompt, message, conv_history)

#tts
out = tts(out)
with open(PATH + "test.mp3", "wb") as f:
    f.write(out)
#stt:
with open(PATH + "test.mp3", "rb") as f:
    bts = f.read()
    print(stt(bts))
"""
    
