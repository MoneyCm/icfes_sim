import streamlit as st
import os
import sys

# Asegurar que los módulos 'db' y 'core' sean visibles desde cualquier nivel
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

def load_css():
    """Carga los estilos premium adaptados para estudiantes (Azul/Naranja ICFES). Mikey"""
    st.markdown("""
    <style>
    :root {
        --icfes-blue: #004b93;
        --icfes-orange: #ff6d00;
        --text-main: #1e293b;
    }
    .stApp {
        background: radial-gradient(circle at top right, #fcfcfc 0%, #f1f5f9 100%);
    }
    .icfes-card {
        background: rgba(255,255,255,0.8);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0,75,147,0.1);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .icfes-header {
        font-weight: 800;
        color: var(--icfes-blue);
        border-left: 5px solid var(--icfes-orange);
        padding-left: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(title="Simulador ICFES 🎓", subtitle="Camino al Puntaje Nacional"):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        # Placeholder para logo
        st.markdown(f"<div style='font-size: 3rem;'>🎓</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1 style='margin:0; color:#004b93;'>{title}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b;'>{subtitle}</p>", unsafe_allow_html=True)

def render_custom_sidebar():
    """Sidebar Académico Multi-usuario. Mikey"""
    from db.session import SessionLocal
    from db.models import UserStats
    from core.auth import AuthManager
    
    db_s = SessionLocal()
    u_id = st.session_state.get("user_id")
    stats_s = None
    
    try:
        if u_id:
            stats_s = db_s.query(UserStats).filter_by(user_id=u_id).first()
            if not stats_s:
                stats_s = UserStats(user_id=u_id, total_points=0)
                db_s.add(stats_s)
                db_s.commit()
                db_s.refresh(stats_s)
        
        if stats_s:
            st.sidebar.markdown(f"""
            <div class="icfes-card" style='text-align: center;'>
                <div style='font-size: 0.8rem; color: #64748b; font-weight: 800;'>Puntaje Acumulado</div>
                <div style='font-size: 2.5rem; color: #ff6d00; font-weight: 800;'>{stats_s.total_points}</div>
                <div style='font-size: 0.7rem; color: #64748b;'>Racha: {stats_s.current_streak}🔥</div>
            </div>
            """, unsafe_allow_html=True)

        st.sidebar.markdown("- 💬 Inglés")
        
        st.sidebar.markdown("### 🛠️ Herramientas")
        st.sidebar.page_link("pages/4_Entrenamiento_Oficial.py", label="Guías Oficiales", icon="📖")
        st.sidebar.page_link("pages/2_Generador_IA.py", label="Generador IA", icon="🤖")
        st.sidebar.page_link("pages/3_Banco_Preguntas.py", label="Mi Banco", icon="📚")
        
        st.sidebar.divider()
        if st.sidebar.button("🚪 Salir"):
            AuthManager.logout()
            
    finally:
        db_s.close()
    
    return stats_s

def metric_card(label, value, sublabel):
    st.markdown(f"""
    <div class="icfes-card" style='text-align: center;'>
        <div style='color: #004b93; font-weight: 800; font-size: 0.8rem;'>{label}</div>
        <div style='font-size: 2rem; font-weight: 800;'>{value}</div>
        <div style='color: #64748b; font-size: 0.7rem;'>{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)
