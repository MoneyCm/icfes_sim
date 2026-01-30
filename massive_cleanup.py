import os
import sys
import unicodedata
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def normalize_text(text):
    if not text: return ""
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return " ".join(text.lower().split())

def perform_cleanup():
    db = SessionLocal()
    try:
        all_q = db.query(Question).all()
        print(f"Iniciando limpieza de {len(all_q)} preguntas...")
        
        # 1. Normalizar Materias
        subject_map = {
            "matematicas": "Matemáticas",
            "lectura critica": "Lectura Crítica",
            "ciencias naturales": "Ciencias Naturales",
            "sociales y ciudadanas": "Sociales y Ciudadanas",
            "ingles": "Inglés"
        }
        
        norm_stems = {} # norm_stem -> [question_id]
        deleted_count = 0
        updated_subjects = 0
        
        for q in all_q:
            # Normalizar materia
            norm_sub = normalize_text(q.subject)
            if norm_sub in subject_map and q.subject != subject_map[norm_sub]:
                q.subject = subject_map[norm_sub]
                updated_subjects += 1
            
            # Revisar duplicados difusos
            n_stem = normalize_text(q.stem)
            if n_stem not in norm_stems:
                norm_stems[n_stem] = q.question_id
            else:
                # Ya existe una versión de esta pregunta, borrar esta
                db.delete(q)
                deleted_count += 1
        
        db.commit()
        print(f"Limpieza completada:")
        print(f"- Materias actualizadas: {updated_subjects}")
        print(f"- Duplicados difusos eliminados: {deleted_count}")
        
        # Conteo final
        final_qs = db.query(Question).all()
        print(f"- Total de preguntas únicas finales: {len(final_qs)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la limpieza: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    perform_cleanup()
