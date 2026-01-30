import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from core.generators.llm import LLMGenerator
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"🔑 API Key detectada: {api_key[:10]}...")
gen = LLMGenerator(api_key=api_key)
print(f"🤖 Modelo configurado en LLMGenerator: {gen.model_name}")

try:
    # Intento de generación mínima
    res = gen.generate_from_text("Hola mundo", num_q=1)
    if res:
        print("✅ Generación exitosa.")
    else:
        print("❌ Generación fallida (vacía).")
except Exception as e:
    print(f"❌ Error durante la generación: {e}")
