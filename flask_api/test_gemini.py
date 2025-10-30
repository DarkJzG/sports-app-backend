import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key encontrada: {api_key[:10]}..." if api_key else "❌ API Key NO encontrada")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-image")
    
    try:
        response = model.generate_content(["A simple red t-shirt on white background"])
        print("✅ Gemini responde correctamente")
        print(f"Candidatos: {len(response.candidates)}")
    except Exception as e:
        print(f"❌ Error: {e}")
