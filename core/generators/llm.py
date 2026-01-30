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
        print(f"LLM: Generando {num_q} de {subject} (Nivel {difficulty}) via {self.provider}")
        num_q = int(num_q)
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
                source_instruction = (
                    "analizando y mimetizando el 'ADN pedagógico', el estilo de redacción, la estructura de las situaciones problema "
                    "y la lógica de distractores presentes en el siguiente texto de referencia. No te limites a preguntar 'sobre' el texto, "
                    "sino que crea nuevas preguntas que parezcan haber sido sacadas de ese mismo documento oficial.\n\n"
                    f"TEXTO DE REFERENCIA (ESTILO Y ESTRUCTURA):\n\"\"\"{context}\"\"\""
                )
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
            5. ESTILO OFICIAL: El enunciado debe presentar una situación contextualizada (caso, gráfica imaginaria, experimento o texto) seguido de una pregunta directa, tal como se muestra en los ejemplos de la guía.
            6. MUY IMPORTANTE: Debes devolver EXACTAMENTE {current_batch} preguntas diferentes en el JSON.
            
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
                        print(f"DEBUG: {self.provider} Raw Response: {response.text[:200]}...")
                        data = json.loads(response.text)
                        batch_questions = data.get("questions", [])
                
                elif self.provider == "Groq":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un experto pedagogo del ICFES. Responde siempre en JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        raw_content = response.choices[0].message.content
                        print(f"DEBUG: {self.provider} Raw Response: {raw_content[:200]}...")
                        data = json.loads(raw_content)
                        # Soportar tanto {"questions": [...]} como [...] directamente o un solo objeto
                        if "questions" in data:
                            batch_questions = data["questions"]
                        elif isinstance(data, list):
                            batch_questions = data
                        else:
                            batch_questions = [data]

                elif self.provider == "Mistral":
                    response = self.client.chat.complete(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un experto pedagogo del ICFES. Responde siempre en JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        raw_content = response.choices[0].message.content
                        print(f"DEBUG: {self.provider} Raw Response: {raw_content[:200]}...")
                        data = json.loads(raw_content)
                        if "questions" in data:
                            batch_questions = data["questions"]
                        elif isinstance(data, list):
                            batch_questions = data
                        else:
                            batch_questions = [data]

                # VALIDACIÓN Y EXTENSIÓN UNIFICADA
                if isinstance(batch_questions, list) and len(batch_questions) > 0:
                    valid_batch = []
                    for q in batch_questions:
                        if not isinstance(q, dict): continue
                        
                        # Normalizar nombres de campos comunes
                        stem = q.get("stem", q.get("pregunta", q.get("enunciado")))
                        options = q.get("options", q.get("alternativas", q.get("opciones")))
                        correct_key = q.get("correct_key", q.get("respuesta", q.get("correct_answer")))
                        rationale = q.get("rationale", q.get("justificacion", ""))
                        if stem and options:
                            valid_batch.append({
                                "stem": stem, "options": options, 
                                "correct_key": correct_key, "rationale": rationale,
                                "topic": q.get("topic", "General"),
                                "competency": q.get("competency", "General")
                            })
                    all_questions.extend(valid_batch)
                    remaining -= len(valid_batch)
                else:
                    msg = f"⚠️ El lote de {self.provider} no devolvió preguntas válidas. Reintentando..."
                    try: st.warning(msg)
                    except: print(msg)
                    time.sleep(2)

            except Exception as e:
                err_msg = str(e)
                if "rate_limit_exceeded" in err_msg or "429" in err_msg:
                    msg = f"⚠️ **Límite de cuota alcanzado en {self.provider}**"
                    try: st.error(msg)
                    except: print(msg)
                else:
                    msg = f"Error en el lote ({self.provider}): {e}"
                    try: st.error(msg)
                    except: print(msg)
                break
        
        return all_questions

    def extract_from_booklet(self, context, subject="Matemáticas", progress_callback=None):
        """
        Lector Especializado: Extrae preguntas OFICIALES y EXPLICADAS de documentos del ICFES.
        A diferencia de la generación, esto busca la verdad literal del documento.
        """
        print(f"LLM: Extrayendo preguntas oficiales de {subject} via {self.provider}")
        
        # Dividimos el contexto en trozos de ~15k chars para no saturar y permitir detalle
        chunk_size = 15000
        chunks = [context[i:i+chunk_size] for i in range(0, len(context), chunk_size)]
        
        extracted_questions = []
        
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(i + 1, len(chunks))

            prompt = f"""
            Eres un extractor de datos de alta precisión. Tu objetivo es encontrar preguntas de opción múltiple del ICFES 
            y sus explicaciones oficiales dentro del TEXTO DE REFERENCIA proporcionado.

            TEXTO DE REFERENCIA:
            \"\"\"{chunk}\"\"\"

            INSTRUCCIONES TÉCNICAS:
            1. Busca patrones de preguntas (Número, Enunciado, Opciones A-D).
            2. Busca la 'Justificación de la respuesta' o 'Explicación'.
            3. Extrae la Competencia y el Componente/Afirmación si están presentes.
            4. Si el texto no contiene una pregunta clara, ignóralo.
            5. La materia es {subject}.

            FORMATO DE SALIDA (JSON ESTRICTO):
            {{
              "questions": [
                {{
                  "subject": "{subject}",
                  "competency": "Competencia extraída",
                  "topic": "Componente o Afirmación",
                  "stem": "Enunciado completo",
                  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
                  "correct_key": "Letra",
                  "rationale": "Explicación técnica detallada (por qué es la correcta y por qué las otras no)"
                }}
              ]
            }}
            """

            try:
                batch = []
                if self.provider == "Gemini":
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    if response and response.text:
                        data = json.loads(response.text)
                        batch = data.get("questions", [])
                
                elif self.provider == "Groq":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un extractor de datos experto. Responde siempre en JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        data = json.loads(response.choices[0].message.content)
                        batch = data.get("questions", [])

                elif self.provider == "Mistral":
                    response = self.client.chat.complete(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Eres un extractor de datos experto. Responde siempre en JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    if response and response.choices:
                        data = json.loads(response.choices[0].message.content)
                        batch = data.get("questions", [])

                # Normalización básica
                for q in batch:
                    if q.get("stem") and q.get("options") and q.get("correct_key"):
                        extracted_questions.append(q)
                
                time.sleep(1) # Rate limit avoidance
            except Exception as e:
                print(f"Error extrayendo chunk {i}: {e}")
                continue

        return extracted_questions

    def analyze_style_dna(self, context, subject="Matemáticas"):
        """
        Analiza un texto oficial y extrae su 'ADN Pedagógico' para usarlo en el futuro.
        """
        print(f"LLM: Analizando ADN de estilo para {subject}")
        prompt = f"""
        Eres un analista pedagógico experto del ICFES. Tu tarea es leer el siguiente documento oficial y extraer su "ADN de Estilo".
        
        TEXTO DE MUESTRA:
        \"\"\"{context[:25000]}\"\"\"
        
        Extrae y resume las siguientes reglas de diseño (ADN) que usas para crear estas preguntas:
        1. ESTRUCTURA DEL ENUNCIADO: ¿Cómo se presentan los problemas? (Gráficos, casos hipotéticos, textos largos, etc.)
        2. COMPLEJIDAD COGNITIVA: ¿Qué tipo de razonamiento se exige? (Inferencial, literal, cálculo directo, análisis de variables).
        3. DISEÑO DE DISTRACTORES: ¿Cómo son las opciones incorrectas? (Errores comunes, verdades a medias, fallas de lógica).
        4. TONO: ¿Es el lenguaje formal, técnico, amigable?
        
        Devuelve SOLO el resumen de estas reglas (el ADN) en un texto plano detallado. Este texto servirá de "System Prompt" para futuras generaciones.
        """
        
        try:
            if self.provider == "Gemini":
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                return response.text if response else ""
            elif self.provider == "Groq":
                response = self.client.chat.completions.create(
                    model=self.model_name, 
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            elif self.provider == "Mistral":
                response = self.client.chat.complete(
                    model=self.model_name, 
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error analizando estilo: {e}")
            return "Estilo genérico ICFES (Error en análisis)"

    def generate_with_style(self, style_dna, num_q=5, subject="Matemáticas", difficulty=2, progress_callback=None):
        """Genera preguntas nuevas usando un ADN de estilo específico."""
        
        # Simplemente inyectamos el ADN como contexto de estilo en el método base
        # Pero modificamos ligeramente el prompt interno. Para no duplicar código masivo, 
        # podemos llamar a generate_from_text pasando el ADN como 'contexto' pero con una flag especial.
        # Por ahora, implementaremos una versión simplificada que reutiliza la lógica original.
        
        return self.generate_from_text(context=style_dna, num_q=num_q, subject=subject, difficulty=difficulty, progress_callback=progress_callback)
