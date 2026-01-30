import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def check_broken_questions():
    db = SessionLocal()
    try:
        all_q = db.query(Question).all()
        broken = []
        for q in all_q:
            is_broken = False
            reasons = []
            if not q.stem or len(q.stem.strip()) < 5:
                is_broken = True
                reasons.append("Stem vacío o muy corto")
            if not q.options_json or not isinstance(q.options_json, dict) or len(q.options_json) < 2:
                is_broken = True
                reasons.append("Opciones inválidas o insuficientes")
            if not q.correct_key or q.correct_key not in (q.options_json or {}):
                is_broken = True
                reasons.append(f"Clave correcta '{q.correct_key}' no está en las opciones")
            
            if is_broken:
                broken.append((q.question_id, q.subject, reasons))
        
        if not broken:
            print("No se encontraron preguntas rotas.")
        else:
            print(f"Se encontraron {len(broken)} preguntas con problemas:")
            for q_id, sub, res in broken:
                print(f"ID: {q_id} | Materia: {sub} | Problemas: {', '.join(res)}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_broken_questions()
