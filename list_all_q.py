import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

db = SessionLocal()
questions = db.query(Question).all()

print(f"📊 Total de preguntas en DB: {len(questions)}")
print("📋 Detalle de preguntas:")
for q in questions:
    print(f"ID: {q.question_id} | Materia: {q.subject} | Tema: {q.topic} | Fecha: {q.created_at}")

db.close()
