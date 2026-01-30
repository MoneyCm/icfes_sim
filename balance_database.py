import os
import sys
import json
import time
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question
from core.generators.llm import LLMGenerator
from dotenv import load_dotenv

load_dotenv()

def balance_subject(subject, target=150, batch_size=5):
    db = SessionLocal()
    api_key = os.getenv("GROQ_API_KEY")
    provider = "Groq"
        
    generator = LLMGenerator(provider=provider, api_key=api_key)
    
    print(f"--- Iniciando balanceo para: {subject} (Usando {provider}) ---")
    
    try:
        for diff in [1, 2, 3]:
            diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[diff]
            
            # Contar actuales
            current = db.query(func.count(Question.question_id)).filter(
                Question.subject == subject, 
                Question.difficulty == diff
            ).scalar()
            
            needed = target - current
            if needed <= 0:
                print(f"Categoría {diff_label} ya está completa ({current}).")
                continue
                
            print(f"Generando {needed} preguntas para {diff_label}...")
            
            while needed > 0:
                num_to_gen = min(needed, batch_size)
                print(f"  Batch: generando {num_to_gen} preguntas...")
                
                questions = generator.generate_from_text(
                    context=None, 
                    num_q=num_to_gen, 
                    subject=subject, 
                    difficulty=diff
                )
                
                if questions:
                    count_saved = 0
                    for q_data in questions:
                        # Guardar en DB
                        try:
                            # Preparar hash para evitar duplicados en la misma carrera
                            import hashlib
                            h = hashlib.sha256(q_data['stem'].strip().lower().encode()).hexdigest()
                            
                            new_q = Question(
                                subject=subject,
                                competency=q_data.get('competency', 'General'),
                                topic=q_data.get('topic', 'General'),
                                difficulty=diff,
                                stem=q_data['stem'],
                                options_json=q_data['options'],
                                correct_key=q_data.get('correct_key', q_data.get('correct_answer')), # Intentar ambos
                                rationale=q_data.get('rationale', ''),
                                hash_norm=h
                            )
                            db.add(new_q)
                            db.commit()
                            count_saved += 1
                        except Exception as e:
                            db.rollback()
                            print(f"    Error guardando pregunta: {e}")
                            continue
                    
                    needed -= count_saved
                    print(f"  Guardadas {count_saved} preguntas. Faltan {needed}.")
                else:
                    print("  Error en la generación del batch. Reintentando...")
                    time.sleep(2)
                
                # Pequeña pausa para no saturar la API
                time.sleep(1)
                
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        balance_subject(sys.argv[1])
    else:
        print("Uso: python balance_database.py <Nombre Materia>")
