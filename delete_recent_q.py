import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

db = SessionLocal()
# Filtrar por el timestamp exacto de la última carga fallida
target_time = "2026-01-30 02:04:17.646351"
deleted = db.query(Question).filter(Question.created_at == target_time).delete(synchronize_session=False)

db.commit()
print(f"🗑️ Se han eliminado {deleted} preguntas basadas en la guía.")
db.close()
