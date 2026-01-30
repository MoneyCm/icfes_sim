import streamlit as st
import sys
import os
import random
import time

# Adaptación para navegación de páginas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Question, Attempt, UserStats
from ui_utils import load_css, render_header, render_custom_sidebar, metric_card
from core.auth import AuthManager

st.set_page_config(page_title="Simulacro | ICFES Sim", page_icon="📝", layout="wide")

if not AuthManager.check_auth():
    st.warning("Por favor inicia sesión.")
    st.stop()

load_css()
render_custom_sidebar()
render_header(title="Nuevo Simulacro 🚀", subtitle="Pon a prueba tus conocimientos")

db = SessionLocal()

# UI DE CONFIGURACIÓN
if "quiz_active" not in st.session_state:
    st.session_state["quiz_active"] = False

if not st.session_state["quiz_active"]:
    with st.container():
        st.markdown("<div class='icfes-card'>", unsafe_allow_html=True)
        st.subheader("⚙️ Configuración del Test")
        
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("¿Qué materia quieres practicar?", ["Todas", "Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"])
        with col2:
            num_q = st.number_input("Número de preguntas", 5, 50, 10)
        
        if st.button("🏁 Iniciar Simulacro", type="primary", use_container_width=True):
            query = db.query(Question)
            if subject != "Todas":
                query = query.filter(Question.subject == subject)
            
            questions = query.all()
            if len(questions) < 1:
                st.error("No hay preguntas suficientes en el sistema para esta materia. ¡Usa el Generador IA primero!")
            else:
                st.session_state["quiz_questions"] = random.sample(questions, min(len(questions), num_q))
                st.session_state["quiz_active"] = True
                st.session_state["current_q_idx"] = 0
                st.session_state["answers"] = {}
                st.session_state["start_time"] = time.time()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # LÓGICA DEL CUESTIONARIO
    questions = st.session_state["quiz_questions"]
    idx = st.session_state["current_q_idx"]
    q = questions[idx]
    
    st.progress((idx + 1) / len(questions), text=f"Pregunta {idx + 1} de {len(questions)}")
    
    st.markdown(f"### {q.subject}")
    st.markdown(f"<div class='icfes-card'><h4 style='color:#004b93;'>{q.stem}</h4></div>", unsafe_allow_html=True)
    
    # Opciones
    ops = q.options_json
    choice = st.radio("Elige tu respuesta:", options=list(ops.keys()), format_func=lambda x: f"{x}) {ops[x]}", key=f"q_{q.question_id}")
    
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if idx > 0:
            if st.button("⬅️ Anterior"):
                st.session_state["current_q_idx"] -= 1
                st.rerun()
    
    with col_nav2:
        if idx < len(questions) - 1:
            if st.button("Siguiente ➡️"):
                st.session_state["answers"][q.question_id] = choice
                st.session_state["current_q_idx"] += 1
                st.rerun()
        else:
            if st.button("✅ Finalizar Simulacro", type="primary"):
                st.session_state["answers"][q.question_id] = choice
                
                # CÁLCULO DE RESULTADOS
                total = len(questions)
                correct = 0
                for quest in questions:
                    ans = st.session_state["answers"].get(quest.question_id)
                    is_right = (ans == quest.correct_key)
                    if is_right: correct += 1
                    
                    # Guardar intento
                    attempt = Attempt(
                        user_id=st.session_state["user_id"],
                        question_id=quest.question_id,
                        chosen_key=ans,
                        is_correct=is_right
                    )
                    db.add(attempt)
                
                # Actualizar puntos
                stats = db.query(UserStats).filter_by(user_id=st.session_state["user_id"]).first()
                points_won = correct * 10
                stats.total_points += points_won
                db.commit()
                
                st.session_state["last_score"] = (correct / total) * 100
                st.session_state["quiz_active"] = False
                st.balloons()
                st.success(f"¡Simulacro Terminado! Puntaje: {correct}/{total} ({st.session_state['last_score']:.1f}%)")
                st.info(f"🏆 ¡Acabas de ganar {points_won} puntos para tu rango!")
                if st.button("🏠 Volver al Inicio"):
                    st.rerun()

db.close()
