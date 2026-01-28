import json
import time
import streamlit as st
from google import genai
from google.genai import types

class LLMGenerator:
    """Motor de IA adaptado para el examen ICFES v1.0. Mikey"""
    def __init__(self, provider="Gemini", api_key="", model_name="gemini-2.0-flash-exp"):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        
        if provider == "Gemini":
            self.client = genai.Client(api_key=api_key)

    def generate_from_text(self, context, num_q=5, subject="Matemáticas", difficulty=2, progress_callback=None):
        """Genera preguntas estilo ICFES (4 opciones) basadas en un texto de referencia. Mikey"""
        
        diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[difficulty]
        
        prompt = f"""
        Eres un experto pedagogo diseñando el examen ICFES (grado 11) para Colombia.
        Tu tarea es crear {num_q} preguntas de selección múltiple basadas EXCLUSIVAMENTE en el siguiente texto de referencia.

        TEXTO DE REFERENCIA:
        \"\"\"{context}\"\"\"

        REGLAS DE ORO (Protocolo ICFES):
        1. MATERIA: {subject}.
        2. DIFICULTAD: {diff_label}.
        3. FORMATO: Cada pregunta DEBE tener:
           - Un enunciado (puedes plantear un caso o situación).
           - 4 OPCIONES MARCADAS COMO A, B, C, D (Solo una correcta).
           - Una justificación técnica de por qué la correcta es la correcta.
        4. ESTILO: Lenguaje académico pero comprensible para estudiantes de 16-18 años.
        
        Devuelve el resultado ÚNICAMENTE como un objeto JSON con la siguiente estructura:
        {{
          "questions": [
            {{
              "subject": "{subject}",
              "topic": "Tema detectado del texto",
              "stem": "Enunciado de la pregunta",
              "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
              "correct_key": "Letra de la correcta (A, B, C o D)",
              "rationale": "Justificación detallada"
            }}
          ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            if response and response.text:
                data = json.loads(response.text)
                return data.get("questions", [])
        except Exception as e:
            st.error(f"Error en la IA: {e}")
            return []
        
        return []
