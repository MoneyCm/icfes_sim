import os
import sys
from sqlalchemy import func
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from db.session import SessionLocal
from db.models import Question

def calculate_balancing_plan():
    db = SessionLocal()
    try:
        results = db.query(
            Question.subject, 
            Question.difficulty, 
            func.count(Question.question_id)
        ).group_by(Question.subject, Question.difficulty).all()
        
        data = {}
        for sub, diff, count in results:
            if sub not in data: data[sub] = {1: 0, 2: 0, 3: 0}
            data[sub][diff] = count
            
        # Encontrar el máximo actual en cualquier celda
        max_in_cell = 0
        for sub in data:
            for diff in data[sub]:
                if data[sub][diff] > max_in_cell:
                    max_in_cell = data[sub][diff]
        
        # Opcional: Redondear al siguiente múltiplo de 10 o 50 para que "todo igual" sea más estético
        target = ((max_in_cell // 10) + 1) * 10 
        if target < 150: target = 150 # Vamos a proponer 150 por celda para que sea sólido
        
        print(f"Target por categoría (Materia + Dificultad): {target}\n")
        print("| Materia | Básico | Intermedio | Avanzado | Total a Agregar |")
        print("| :--- | :---: | :---: | :---: | :---: |")
        
        grand_needed = 0
        for sub in ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"]:
            row = data.get(sub, {1: 0, 2: 0, 3: 0})
            needed_b = max(0, target - row[1])
            needed_i = max(0, target - row[2])
            needed_a = max(0, target - row[3])
            sub_total_needed = needed_b + needed_i + needed_a
            grand_needed += sub_total_needed
            
            print(f"| {sub} | +{needed_b} | +{needed_i} | +{needed_a} | **{sub_total_needed}** |")
            
        print(f"\nTOTAL GLOBAL A GENERAR: {grand_needed}")
        print(f"BOTE FINAL: {target * 15} preguntas")
        
    finally:
        db.close()

if __name__ == "__main__":
    calculate_balancing_plan()
