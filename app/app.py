import streamlit as st
import sys
import os

# Adaptación de rutas para el nuevo ecosistema ICFES
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from db.session import SessionLocal, init_db
from db.models import User, UserStats
from ui_utils import load_css, render_header, render_custom_sidebar, metric_card
from core.auth import AuthManager

st.set_page_config(page_title="ICFES Sim 🎓", page_icon="🎓", layout="wide")

# Inicializar DB en el primer arranque
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True

load_css()

if not AuthManager.check_auth():
    render_header(title="ICFES Sim: Tu Pasaporte Universitario", subtitle="Inicia sesión para empezar a practicar")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔑 Entrar")
        with st.form("login_form"):
            user_in = st.text_input("Usuario")
            pass_in = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar", use_container_width=True):
                if AuthManager.login(user_in, pass_in):
                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    
    with col2:
        st.subheader("📝 Crear Cuenta")
        with st.form("reg_form"):
            new_user = st.text_input("Nombre de Usuario")
            new_pass = st.text_input("Elegir Contraseña", type="password")
            if st.form_submit_button("Registrarme", use_container_width=True):
                db = SessionLocal()
                if db.query(User).filter_by(username=new_user).first():
                    st.error("El usuario ya existe")
                else:
                    user = User(username=new_user, password_hash=AuthManager.hash_password(new_pass))
                    db.add(user)
                    db.commit()
                    st.success("¡Cuenta creada! Ya puedes entrar.")
                db.close()
    st.stop()

# DASHBOARD PARA ESTUDIANTES
stats = render_custom_sidebar()
render_header()

st.markdown(f"### 🎯 ¡Hola, {st.session_state['username']}!")
st.info("Este es tu centro de entrenamiento para el examen ICFES. Aquí podrás practicar por materias y mejorar tu puntaje.")

# Métricas rápidas
c1, c2, c3 = st.columns(3)
with c1:
    metric_card("Materias Dominadas", "0/5", "Vamos por todas")
with c2:
    metric_card("Preguntas Respondidas", "0", "Hoy es un buen día")
with c3:
    metric_card("Puntaje Global Est.", "100/500", "Meta: 400+")

st.divider()
st.markdown("### 🚀 Acciones Rápidas")
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.page_link("pages/1_Nuevo_Simulacro.py", label="Nuevo Simulacro", icon="🚀", use_container_width=True)
with col_b:
    st.page_link("pages/4_Entrenamiento_Oficial.py", label="Entrenamiento Oficial", icon="📖", use_container_width=True)
with col_c:
    st.page_link("pages/2_Generador_IA.py", label="Generador IA", icon="🤖", use_container_width=True)
with col_d:
    st.page_link("pages/3_Banco_Preguntas.py", label="Mi Banco", icon="📚", use_container_width=True)

st.divider()
st.markdown("### 🏆 Ranking de Amigos")
db_r = SessionLocal()
top_users = db_r.query(User, UserStats).join(UserStats).order_by(UserStats.total_points.desc()).limit(5).all()
db_r.close()

if top_users:
    for i, (u_obj, s_obj) in enumerate(top_users):
        medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, "👤")
        st.markdown(f"{medal} **{u_obj.username}**: {s_obj.total_points} pts")
else:
    st.info("Aún no hay puntos registrados. ¡Sé el primero en el podio!")
