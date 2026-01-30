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
        --text-muted: #64748b;
    }
    /* =========================================
       FIX IPHONE / DARK MODE: FORZAR TEMA CLARO
       ========================================= */
    
    /* 1. Fondo Global */
    .stApp {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }

    /* 2. Textos Globales (Headers, Párrafos, Markdown, Spans) */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div {
        color: #1e293b !important;
        text-shadow: none !important;
    }

    /* 3. Inputs y Widgets (Evitar fondo negro con letra blanca) */
    .stTextInput input, .stSelectbox, .stMultiSelect {
        color: #1e293b !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* 4. Sidebar (Forzar claro) */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #1e293b !important;
    }
    
    /* 5. Radio Buttons y Checkboxes */
    div[role="radiogroup"] label p {
        color: #1e293b !important;
        font-weight: 500 !important;
    }

    .icfes-card {
        background: white !important;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: var(--text-main) !important;
    }
    
    .icfes-header {
        font-weight: 800;
        color: var(--icfes-blue) !important;
        border-left: 5px solid var(--icfes-orange);
        padding-left: 15px;
        margin-bottom: 10px;
    }

    /* Asegurar que el sidebar no se pierda */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
    }
    /* Estilos para las tarjetas de materias (Caja de Herramientas style) */
    .subject-card {
        background: white !important;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        text-align: left;
        position: relative;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s;
    }
    .subject-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .subject-icon {
        position: absolute;
        top: 15px;
        right: 15px;
        width: 50px;
        height: 50px;
        background: #f3f4f6;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        border: 2px solid #e5e7eb;
    }
    .subject-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }
    .subject-desc {
        font-size: 0.875rem;
        color: #4b5563;
        line-height: 1.25rem;
        margin-bottom: 16px;
    }
    .subject-btn {
        background-color: #ef4444; /* Rojo ICFES soft */
        color: white !important;
        padding: 8px 16px;
        border-radius: 9999px;
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
        border: none;
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
