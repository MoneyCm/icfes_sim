import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

db = SessionLocal()

# Palabras clave de la guía de orientación que no son académicas
keywords = [
    "Estructura", "Structure", "Adjustments", "Booklet", "Cuadernillo", 
    "Sesión", "Session", "Examen", "Exam", "Carga horaria", "Distribución"
]

# También podemos filtrar por la fecha de hoy 2026-01-30 (fecha del sistema en los logs)
# O simplemente borrar las que tengan esas palabras en el tema.

total_deleted = 0
for kw in keywords:
    count = db.query(Question).filter(Question.topic.ilike(f"%{kw}%")).delete(synchronize_session=False)
    total_deleted += count

db.commit()
print(f"🗑️ Se han eliminado un total de {total_deleted} preguntas detectadas como 'orientación'.")
db.close()
