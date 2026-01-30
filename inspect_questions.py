import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def check_english_questions():
    db = SessionLocal()
    try:
        questions = db.query(Question).filter(Question.subject == 'Inglés').order_by(Question.created_at.desc()).limit(10).all()
        
        print(f"--- REVISIÓN DE ÚLTIMAS 10 PREGUNTAS DE INGLÉS ---")
        for q in questions:
            print(f"ID: {q.question_id} | Dificultad: {q.difficulty}")
            print(f"Pregunta: {q.stem[:200]}...")
            print(f"Opciones: {q.options_json}")
            print(f"Correcta: {q.correct_key}")
            print("-" * 30)
            
    finally:
        db.close()

if __name__ == "__main__":
    check_english_questions()
