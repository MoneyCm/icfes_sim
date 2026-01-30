import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

db = SessionLocal()
count = db.query(Question).delete()
db.commit()
print(f"🗑️ Base de datos limpiada. Se eliminaron {count} preguntas en total.")
db.close()
