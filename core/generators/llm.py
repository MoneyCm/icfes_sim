import json
import time
import streamlit as st
from google import genai
from google.genai import types

class LLMGenerator:
    """Motor de IA adaptado para el examen ICFES v1.0. Mikey"""
    def __init__(self, provider="Gemini", api_key="", model_name="gemini-2.5-flash"):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        
        if provider == "Gemini":
            self.client = genai.Client(api_key=api_key)

    def generate_from_text(self, context=None, num_q=5, subject="Matemáticas", difficulty=2, progress_callback=None):
        """Genera preguntas estilo ICFES (4 opciones). Si hay context, lo usa; si no, usa su conocimiento. Mikey"""
        
        diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[difficulty]
        
        if context:
            source_instruction = f"basadas EXCLUSIVAMENTE en el siguiente texto de referencia:\n\nTEXTO DE REFERENCIA:\n\"\"\"{context}\"\"\""
        else:
            source_instruction = "basadas en tu amplio conocimiento pedagógico sobre los temas evaluados en el ICFES para esta materia."

        prompt = f"""
        Eres un experto pedagogo diseñando el examen ICFES (grado 11) para Colombia.
        Tu tarea es crear {num_q} preguntas de selección múltiple {source_instruction}

        REGLAS DE ORO (Protocolo ICFES):
        1. MATERIA: {subject}.
        2. DIFICULTAD: {diff_label}.
        3. FORMATO: Cada pregunta DEBE tener:
           - Un enunciado (puedes plantear un caso o situación o usar conceptos base).
           - 4 OPCIONES MARCADAS COMO A, B, C, D (Solo una correcta).
           - Una justificación técnica de por qué la correcta es la correcta.
        4. ESTILO: Lenguaje académico pero comprensible para estudiantes de 16-18 años.
        
        Devuelve el resultado ÚNICAMENTE como un objeto JSON con la siguiente estructura:
        {{
          "questions": [
            {{
              "subject": "{subject}",
              "competency": "Competencia evaluada (ej: Razonamiento, Uso del conocimiento)",
              "topic": "Tema específico de la pregunta",
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
