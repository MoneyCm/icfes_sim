import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def cleanup_duplicates():
    db = SessionLocal()
    try:
        # Encontrar duplicados por stem
        from sqlalchemy import func
        duplicates = db.query(
            Question.stem, 
            func.count(Question.stem).label('count')
        ).group_by(Question.stem).having(func.count(Question.stem) > 1).all()
        
        deleted_count = 0
        for d in duplicates:
            # Obtener todas las preguntas con ese stem
            qs = db.query(Question).filter(Question.stem == d.stem).all()
            # Dejar la primera, borrar las demás
            for q_to_del in qs[1:]:
                db.delete(q_to_del)
                deleted_count += 1
        
        db.commit()
        print(f"Se eliminaron {deleted_count} preguntas duplicadas.")
        
    except Exception as e:
        db.rollback()
        print(f"Error al limpiar duplicados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
