import os
import sys
import unicodedata
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def normalize_text(text):
    if not text: return ""
    # Quitar acentos, pasar a minúsculas, quitar espacios extras
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return " ".join(text.lower().split())

def exhaustive_audit():
    db = SessionLocal()
    try:
        all_q = db.query(Question).all()
        print(f"Auditoria exhaustiva sobre {len(all_q)} preguntas...")
        
        # 1. Normalización de Materias
        subjects = {}
        for q in all_q:
            norm_sub = normalize_text(q.subject)
            if norm_sub not in subjects: subjects[norm_sub] = []
            subjects[norm_sub].append(q.subject)
        
        print("\n--- Revisión de Materias ---")
        for norm, originals in subjects.items():
            unique_originals = set(originals)
            if len(unique_originals) > 1:
                print(f"ALERTA: Materia inconsistente detectada para '{norm}': {unique_originals}")
            else:
                print(f"Materia '{list(unique_originals)[0]}': {len(originals)} preguntas")

        # 2. Búsqueda de Duplicados Difusos (Fuzzy)
        stems = {}
        for q in all_q:
            norm_stem = normalize_text(q.stem)
            if norm_stem not in stems: stems[norm_stem] = []
            stems[norm_stem].append(q.question_id)
        
        fuzzy_duplicates = {k: v for k, v in stems.items() if len(v) > 1}
        print(f"\n--- Duplicados Difusos ---")
        if not fuzzy_duplicates:
            print("No se encontraron duplicados difusos.")
        else:
            print(f"Se encontraron {len(fuzzy_duplicates)} grupos de duplicados difusos (mismo texto ignorando mayúsculas/acentos).")
            for norm, ids in fuzzy_duplicates.items():
                print(f"Contenido: {norm[:100]}... | IDs: {ids}")

        # 3. Revisión de Calidad (Inglés)
        eng_q = [q for q in all_q if normalize_text(q.subject) == 'ingles']
        print(f"\n--- Calidad de Inglés ({len(eng_q)} preguntas) ---")
        # Ya vimos que hay 30. Revisemos si hay algo "extraño" en sus stems.
        for q in eng_q[:5]:
            print(f"- {q.stem[:50]}...")

    finally:
        db.close()

if __name__ == "__main__":
    exhaustive_audit()
