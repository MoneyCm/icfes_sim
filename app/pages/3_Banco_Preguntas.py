import streamlit as st
import sys
import os
import pandas as pd
import io
import datetime

# Adaptación para navegación de páginas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from db.session import SessionLocal
from db.models import Question
from ui_utils import load_css, render_header, render_custom_sidebar
from core.auth import AuthManager

st.set_page_config(page_title="Banco de Preguntas | ICFES Sim", page_icon="📚", layout="wide")

if not AuthManager.check_auth():
    st.warning("Por favor inicia sesión.")
    st.stop()

load_css()
render_custom_sidebar()
render_header(title="Banco de Preguntas 📚", subtitle="Gestiona y revisa tus desafíos académicos")

db = SessionLocal()

# Filtros Profesionales
col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
with col_f1:
    search = st.text_input("🔍 Buscar en el enunciado...", placeholder="Ej: Pitágoras, Células, Revolución...")
with col_f2:
    subject_f = st.selectbox("Materia", ["Todas", "Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"])
with col_f3:
    diff_f = st.multiselect("Dificultad", [1, 2, 3], format_func=lambda x: {1: "🟢 Básico", 2: "🟡 Intermedio", 3: "🔴 Avanzado"}[x])

# Query inteligente
query = db.query(Question)
if search:
    query = query.filter(Question.stem.ilike(f"%{search}%"))
if subject_f != "Todas":
    query = query.filter(Question.subject == subject_f)
if diff_f:
    query = query.filter(Question.difficulty.in_(diff_f))

questions = query.all()

st.info(f"📚 Mostrando **{len(questions)}** preguntas disponibles en el sistema.")

if not questions:
    st.warning("No se encontraron preguntas con los filtros seleccionados.")
else:
    for q in questions:
        icon = {1: "🟢", 2: "🟡", 3: "🔴"}[q.difficulty]
        with st.expander(f"{icon} [{q.subject}] {q.stem[:80]}..."):
            st.markdown(f"**Enunciado:**\n{q.stem}")
            
            ops = q.options_json
            if ops:
                c1, c2 = st.columns(2)
                for i, (k, v) in enumerate(ops.items()):
                    with (c1 if i % 2 == 0 else c2):
                        st.write(f"**{k})** {v}")
            
            st.markdown(f"**Respuesta Correcta:** :green[{q.correct_key}]")
            if q.rationale:
                st.info(f"💡 **Justificación:** {q.rationale}")
            
            if st.button("🗑️ Eliminar", key=f"del_{q.question_id}", type="secondary"):
                db.delete(q)
                db.commit()
                st.rerun()

db.close()
