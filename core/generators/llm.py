import json
import time
import streamlit as st
from google import genai
from google.genai import types
from groq import Groq
from mistralai import Mistral

class LLMGenerator:
    """Motor de IA adaptado para el examen ICFES v1.0. Mikey"""
    def __init__(self, provider="Gemini", api_key="", model_name=None):
        self.provider = provider
        self.api_key = api_key
        
        if provider == "Gemini":
            self.model_name = model_name if model_name else "gemini-2.5-flash"
            self.client = genai.Client(api_key=api_key)
        elif provider == "Groq":
            self.model_name = model_name if model_name else "llama-3.3-70b-versatile"
            self.client = Groq(api_key=api_key)
        elif provider == "Mistral":
            self.model_name = model_name if model_name else "mistral-large-latest"
            self.client = Mistral(api_key=api_key)

    def generate_from_text(self, context=None, num_q=5, subject="Matemáticas", difficulty=2, progress_callback=None):
        """Genera preguntas estilo ICFES (4 opciones) con soporte para lotes grandes. Mikey"""
        
        diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[difficulty]
        all_questions = []
        
        # Batching: Máximo 10 preguntas por llamada para evitar truncamiento
        batch_size = 5 if num_q > 15 else num_q
        remaining = num_q
        
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            
            if progress_callback:
                progress_callback(len(all_questions), num_q)
            
            if context:
                source_instruction = f"basadas EXCLUSIVAMENTE en el siguiente texto de referencia:\n\nTEXTO DE REFERENCIA:\n\"\"\"{context}\"\"\""
            else:
                source_instruction = "basadas en tu amplio conocimiento pedagógico sobre los temas evaluados en el ICFES para esta materia."

            lang_instruction = ""
            if subject == "Inglés":
                lang_instruction = """
                ESPECIFICACIÓN PARA INGLÉS (ESTRICTO):
                - El enunciado (stem) DEBE estar 100% en INGLÉS.
                - Las 4 opciones (A, B, C, D) DEBEN estar 100% en INGLÉS.
                - ÚNICAMENTE la justificación (rationale) y el tema (topic) deben estar en ESPAÑOL.
                """

            prompt = f"""
            Eres un experto pedagogo diseñando el examen ICFES (grado 11) para Colombia.
            Tu tarea es crear EXACTAMENTE {current_batch} preguntas de selección múltiple {source_instruction}

            REGLAS DE ORO (Protocolo ICFES):
            1. MATERIA: {subject}.
            2. DIFICULTAD: {diff_label}. {lang_instruction}
            3. ALEATORIEDAD: Distribuye la respuesta correcta de forma aleatoria entre A, B, C y D.
            4. FORMATO: Cada pregunta DEBE tener un enunciado, 4 opciones (A-D) y una justificación técnica.
            5. MUY IMPORTANTE: Debes devolver EXACTAMENTE {current_batch} preguntas diferentes en el JSON.
            
            Devuelve el resultado ÚNICAMENTE como un objeto JSON con la siguiente estructura:
            {{
              "questions": [
                {{
                  "subject": "{subject}",
                  "competency": "Competencia evaluada",
                  "topic": "Tema específico",
                  "stem": "Enunciado",
                  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
                  "correct_key": "Letra correcta",
                  "rationale": "Justificación"
                }}
              ]
            }}
            """

            try:
                batch_questions = []
                if self.provider == "Gemini":
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    if response and response.text:
                        data = json.loads(response.text)
                        batch_questions = data.get("questions", [])
                
                elif self.provider == "Groq":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un experto pedagogo del ICFES. Responde siempre con el número exacto de preguntas solicitado en JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        data = json.loads(response.choices[0].message.content)
                        batch_questions = data.get("questions", [])

                elif self.provider == "Mistral":
                    response = self.client.chat.complete(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un experto pedagogo del ICFES. Responde siempre con el número exacto de preguntas en formato JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        data = json.loads(response.choices[0].message.content)
                        batch_questions = data.get("questions", [])

                all_questions.extend(batch_questions)
                remaining -= len(batch_questions)
                
                # Si la IA no genera nada o genera 0, evitamos bucle infinito
                if len(batch_questions) == 0:
                    break
                    
            except Exception as e:
                err_msg = str(e)
                if "rate_limit_exceeded" in err_msg or "429" in err_msg:
                    st.error(f"⚠️ **Límite de cuota alcanzado en {self.provider}**")
                    st.info("💡 Tu cuota diaria gratuita se ha agotado. Te recomiendo **cambiar al otro proveedor** para seguir practicando.")
                else:
                    st.error(f"Error en el lote ({self.provider}): {e}")
                break
        
        return all_questions
