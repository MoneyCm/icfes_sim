import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from core.generators.llm import LLMGenerator
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
gen = LLMGenerator(provider="Groq", api_key=api_key)

print("🧪 Final check for INGLÉS...")
questions = gen.generate_from_text(num_q=2, subject="Inglés", difficulty=2)

if questions:
    for i, q in enumerate(questions):
        print(f"\n--- Q{i+1} ---")
        print(f"Topic: {q.get('topic')}")
        print(f"Stem: {q.get('stem')}")
        print(f"Options: {q.get('options')}")
        print(f"Correcta: {q.get('correct_key')}")
        print(f"Rationale: {q.get('rationale')}")
else:
    print("❌ Error")
