import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    print("--- Testing Gemini ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: No GEMINI_API_KEY found")
        return
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Use a known stable model name
            contents="Genera 1 pregunta de ciencias naturales para el ICFES en JSON.",
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        print("Gemini Response Received!")
        print(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")

def test_groq():
    print("\n--- Testing Groq ---")
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: No GROQ_API_KEY found")
        return
        
    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Genera 1 pregunta de ciencias naturales para el ICFES en JSON."}],
            response_format={"type": "json_object"}
        )
        print("Groq Response Received!")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")

if __name__ == "__main__":
    test_gemini()
    test_groq()
