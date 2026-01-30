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
    
    verified_tag = "🛡️ **PREGUNTA OFICIAL**" if q.is_verified else ""
    st.markdown(f"### {q.subject} {verified_tag}")
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
                st.session_state["show_results"] = True
                st.session_state["last_results_data"] = {
                    "total": total,
                    "correct": correct,
                    "points": points_won,
                    "summary_questions": questions,
                    "user_answers": st.session_state["answers"]
                }
                st.balloons()
                st.rerun()

# MOSTRAR RESULTADOS DETALLADOS
if "show_results" in st.session_state and st.session_state["show_results"]:
    res = st.session_state["last_results_data"]
    
    st.markdown("<div class='icfes-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.header("📊 Resultados del Simulacro")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        metric_card("Preguntas", f"{res['correct']}/{res['total']}", "Total contestadas")
    with col_r2:
        metric_card("Puntaje", f"{(res['correct']/res['total'])*100:.1f}%", "Efectividad")
    with col_r3:
        metric_card("Puntos Ganados", f"+{res['points']}", "Bonus académico")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📝 Revisión Detallada")
    
    for i, q in enumerate(res["summary_questions"]):
        ans = res["user_answers"].get(q.question_id)
        is_correct = (ans == q.correct_key)
        
        status_icon = "✅" if is_correct else "❌"
        status_color = "#d4edda" if is_correct else "#f8d7da"
        status_border = "#c3e6cb" if is_correct else "#f5c6cb"
        
        verified_badge = "🛡️ OFICIAL" if q.is_verified else ""
        with st.expander(f"{status_icon} {verified_badge} Pregunta {i+1}: {q.topic}"):
            st.markdown(f"**{q.stem}**")
            ops = q.options_json
            for k, v in ops.items():
                if k == q.correct_key:
                    st.markdown(f"🟢 **{k}) {v}** (Correcta)")
                elif k == ans and not is_correct:
                    st.markdown(f"🔴 **{k}) {v}** (Tu elección)")
                else:
                    st.write(f"{k}) {v}")
            
            st.divider()
            st.info(f"💡 **Explicación:** {q.rationale}")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Nuevo Simulacro", use_container_width=True):
            del st.session_state["show_results"]
            st.rerun()
    with col_btn2:
        if st.button("🏠 Ir al Dashboard", type="primary", use_container_width=True):
            del st.session_state["show_results"]
            st.switch_page("app.py")

db.close()
