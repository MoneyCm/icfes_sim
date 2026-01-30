import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

db = SessionLocal()
# Obtener las últimas 10 preguntas
questions = db.query(Question).order_by(Question.created_at.desc()).limit(10).all()

print("📋 Últimas preguntas en la base de datos:")
for q in questions:
    print(f"ID: {q.question_id} | Tema: {q.topic} | Fecha: {q.created_at}")

db.close()
