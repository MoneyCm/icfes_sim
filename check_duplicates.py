import os
import sys
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def find_duplicates():
    db = SessionLocal()
    try:
        # Contar duplicados por hash_norm
        duplicates = db.query(
            Question.hash_norm, 
            func.count(Question.hash_norm).label('count')
        ).group_by(Question.hash_norm).having(func.count(Question.hash_norm) > 1).all()
        
        if not duplicates:
            print("No se encontraron duplicados por hash_norm.")
        else:
            print(f"Se encontraron {len(duplicates)} grupos de duplicados.")
            for d in duplicates:
                print(f"Hash: {d.hash_norm} | Cantidad: {d.count}")
                
        # También revisar stem por si acaso el hash falló
        stem_duplicates = db.query(
            Question.stem, 
            func.count(Question.stem).label('count')
        ).group_by(Question.stem).having(func.count(Question.stem) > 1).all()
        
        if stem_duplicates:
            print(f"\nSe encontraron {len(stem_duplicates)} grupos con el mismo enunciado (stem).")
            for d in stem_duplicates:
                print(f"Stem: {d.stem[:100]}... | Cantidad: {d.count}")
                
    finally:
        db.close()

if __name__ == "__main__":
    find_duplicates()
