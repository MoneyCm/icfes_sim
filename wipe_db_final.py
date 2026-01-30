import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question, Attempt

db = SessionLocal()
try:
    # Eliminar primero los intentos por la relación FK
    db.query(Attempt).delete()
    count = db.query(Question).delete()
    db.commit()
    print(f"🗑️ Base de datos purgada. Se eliminaron {count} preguntas y todos los intentos.")
except Exception as e:
    db.rollback()
    print(f"❌ Error al purgar: {e}")
finally:
    db.close()
