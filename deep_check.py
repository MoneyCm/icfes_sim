import os
import sys
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def deep_check():
    db = SessionLocal()
    try:
        # 1. Materias únicas
        subjects = db.query(Question.subject, func.count(Question.subject)).group_by(Question.subject).all()
        print("Materias en DB:")
        for s, c in subjects:
            print(f"- {s}: {c}")
            
        # 2. Fecha de creación (más recientes)
        latest = db.query(Question).order_by(Question.created_at.desc()).limit(5).all()
        print("\nÚltimas 5 preguntas creadas:")
        for q in latest:
            print(f"- {q.subject} | {q.created_at} | {q.stem[:50]}...")
            
        # 3. Datos nulos en campos importantes
        null_rationales = db.query(func.count(Question.question_id)).filter(Question.rationale == None).scalar()
        print(f"\nPreguntas sin 'rationale' (explicación): {null_rationales}")
        
    finally:
        db.close()

if __name__ == "__main__":
    deep_check()
