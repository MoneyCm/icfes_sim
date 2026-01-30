import os
import sys
import json
import time
import hashlib
import unicodedata
from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime, JSON, func
from sqlalchemy.orm import sessionmaker, declarative_base
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

# Configuración de DB
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    question_id = Column(String(36), primary_key=True)
    subject = Column(String)
    competency = Column(String)
    topic = Column(String)
    difficulty = Column(Integer)
    stem = Column(Text)
    options_json = Column(JSON)
    correct_key = Column(String)
    rationale = Column(Text)
    hash_norm = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    is_verified = Column(Boolean, default=False)
    global_hits = Column(Integer, default=0)
    global_misses = Column(Integer, default=0)

def normalize_text(text):
    if not text: return ""
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return " ".join(text.lower().split())

def balance():
    db = SessionLocal()
    
    # Intentar Mistral ya que Groq/Gemini están agotados
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key:
        print("--- Usando MISTRAL para balanceo ESTRICTO (Target: 250) ---")
        client = Mistral(api_key=mistral_key)
        provider = "Mistral"
        model = "mistral-large-latest"
    else:
        print("Error: No se encontró MISTRAL_API_KEY")
        return
    
    subjects = ["Ciencias Naturales", "Inglés", "Sociales y Ciudadanas", "Matemáticas", "Lectura Crítica"]
    target = 250 # Objetivo para igualar todas las categorías
    
    for sub in subjects:
        for diff in [1, 2, 3]:
            diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[diff]
            
            # 1. Obtener todas las preguntas actuales para esta categoría
            current_qs = db.query(Question).filter(
                Question.subject == sub, 
                Question.difficulty == diff
            ).order_by(Question.created_at.desc()).all()
            
            count = len(current_qs)
            
            # 2. Recortar si sobran (Mantener las más nuevas/mejores)
            if count > target:
                to_delete = count - target
                print(f"[{sub}] {diff_label}: Sobran {to_delete}. Recortando para tener exactamente {target}...")
                # Las que sobran son las más viejas (al final de la lista ordenada por desc)
                for q_extra in current_qs[target:]:
                    db.delete(q_extra)
                db.commit()
                print(f"  Recorte completado. Ahora hay {target}.")
                count = target

            # 3. Generar si faltan
            needed = target - count
            if needed <= 0:
                print(f"[{sub}] {diff_label} ya está equilibrada en {count}.")
                continue
            
            print(f"[{sub}] {diff_label}: Faltan {needed} para llegar a {target}. Generando...")
            
            consecutive_zeros = 0
            while needed > 0 and consecutive_zeros < 3:
                batch = min(needed, 10)
                prompt = (
                    f"Eres un experto pedagogo del ICFES. Genera {batch} preguntas ÚNICAS y ORIGINALES de {sub} ({diff_label}).\n"
                    "Responde estrictamente en JSON:\n"
                    '{"questions": [{"topic": "...", "stem": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_key": "Letra", "rationale": "..."}]}'
                )
                
                try:
                    response = client.chat.complete(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    raw_content = response.choices[0].message.content
                    data = json.loads(raw_content)
                    qs = data.get("questions", [])
                    if not qs and isinstance(data, list): qs = data
                    if not qs and "questions" not in data: qs = [data]
                    
                    added_in_batch = 0
                    for q in qs:
                        stem = q.get("stem", q.get("pregunta", q.get("enunciado")))
                        options = q.get("options", q.get("alternativas", q.get("opciones")))
                        if not stem or not options: continue
                        
                        h = hashlib.sha256(normalize_text(stem).encode()).hexdigest()
                        try:
                            import uuid
                            new_q = Question(
                                question_id=str(uuid.uuid4()),
                                subject=sub,
                                competency=q.get("competency", "General"),
                                topic=q.get("topic", "General"),
                                difficulty=diff,
                                stem=stem,
                                options_json=options,
                                correct_key=q.get("correct_key", q.get("respuesta", "A")),
                                rationale=q.get("rationale", ""),
                                hash_norm=h
                            )
                            db.add(new_q)
                            db.commit()
                            added_in_batch += 1
                        except Exception:
                            db.rollback()
                            continue
                    
                    needed -= added_in_batch
                    if added_in_batch == 0:
                        consecutive_zeros += 1
                    else:
                        consecutive_zeros = 0
                    
                    print(f"  Guardadas {added_in_batch}. Faltan {needed}.")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Error: {e}")
                    break
            
            if consecutive_zeros >= 3:
                print(f"  SALTANDO {sub} {diff_label} por exceso de duplicados.")

    db.close()

if __name__ == "__main__":
    balance()
