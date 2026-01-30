import os
import sys
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def final_stats():
    db = SessionLocal()
    try:
        # Estadísticas por materia y dificultad
        results = db.query(
            Question.subject, 
            Question.difficulty, 
            func.count(Question.question_id)
        ).group_by(Question.subject, Question.difficulty).order_by(Question.subject, Question.difficulty).all()
        
        print("| Materia | Dificultad | Cantidad |")
        print("| :--- | :--- | :--- |")
        
        summary = {}
        for sub, diff, count in results:
            diff_label = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}.get(diff, str(diff))
            print(f"| {sub} | {diff_label} | {count} |")
            
            if sub not in summary: summary[sub] = {"Básico": 0, "Intermedio": 0, "Avanzado": 0, "Total": 0}
            summary[sub][diff_label] = summary[sub].get(diff_label, 0) + count
            summary[sub]["Total"] += count
            
        print("\nTOTALES:")
        grand_total = 0
        for sub, stats in summary.items():
            print(f"{sub}: {stats['Total']} ({stats})")
            grand_total += stats['Total']
        print(f"GRAND TOTAL: {grand_total}")
        
    finally:
        db.close()

if __name__ == "__main__":
    final_stats()
