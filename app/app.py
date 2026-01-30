import streamlit as st
import sys
import os

# Adaptación de rutas para el nuevo ecosistema ICFES (Fix para Cloud)
# Agregamos el directorio raíz al path para que encuentre 'db' y 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal, init_db
from db.models import User, UserStats, Question, Attempt
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
st.info("Bienvenido a la **Caja de Herramientas ICFES**. Aquí tienes todo lo necesario para alcanzar tu meta.")

# Métricas de la Base de Datos
db_dash = SessionLocal()
total_q = db_dash.query(Question).count()
answered_q = db_dash.query(Attempt).filter_by(user_id=st.session_state['user_id']).count()
db_dash.close()

col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Fondo de Saberes", f"{total_q}", "Preguntas disponibles")
with col2:
    metric_card("Tu Progreso", f"{answered_q}", "Ejercicios realizados")
with col3:
    metric_card("Puntaje Global", f"{stats.total_points if stats else 0} pts", "Nivel: Aspirante")

st.markdown("---")
st.subheader("🛠️ Caja de Herramientas")

subjects_data = [
    {"name": "Lectura Crítica", "icon": "📖", "desc": "Fortalece tu comprensión de textos y análisis literario."},
    {"name": "Matemáticas", "icon": "📐", "desc": "Domina el razonamiento cuantitativo y la resolución de problemas."},
    {"name": "Sociales y Ciudadanas", "icon": "🌍", "desc": "Analiza contextos históricos, políticos y ciudadanos."},
    {"name": "Ciencias Naturales", "icon": "🧪", "desc": "Explora fenómenos biológicos, físicos y químicos."},
    {"name": "Inglés", "icon": "🇬🇧", "desc": "Mejora tus habilidades comunicativas en lengua extranjera."}
]

# Grid de 3 columnas
cols = st.columns(3)
for i, sub in enumerate(subjects_data):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="subject-card">
            <div class="subject-icon">{sub['icon']}</div>
            <div>
                <div class="subject-title">{sub['name']}</div>
                <div class="subject-desc">{sub['desc']}</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <a href="/Nuevo_Simulacro" target="_self" class="subject-btn">Práctica Rápida</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Nota: Los links internos en Streamlit a veces requieren query params o st.page_link para funcionar bien.
        # Usamos st.page_link para mayor confiabilidad debajo del HTML
        st.page_link("pages/1_Nuevo_Simulacro.py", label=f"Entrenar {sub['name']}", icon=sub['icon'])

st.divider()
st.markdown("### 🏆 Ranking Regional")
db_r = SessionLocal()
top_users = db_r.query(User, UserStats).join(UserStats).order_by(UserStats.total_points.desc()).limit(5).all()
db_r.close()

if top_users:
    cols_rank = st.columns(5)
    for i, (u_obj, s_obj) in enumerate(top_users):
        with cols_rank[i]:
            medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, "👤")
            st.markdown(f"""
            <div class="icfes-card" style='text-align:center;'>
                <div style='font-size: 2rem;'>{medal}</div>
                <div style='font-weight: 700;'>{u_obj.username}</div>
                <div style='color: #ff6d00; font-weight: 800;'>{s_obj.total_points}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Aún no hay puntos registrados. ¡Sé el primero!")
