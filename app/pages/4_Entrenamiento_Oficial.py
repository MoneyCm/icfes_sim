import streamlit as st
import sys
import os
import hashlib

# Adaptación para navegación de páginas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Question
from ui_utils import load_css, render_header, render_custom_sidebar
from core.pdf_utils import get_pdf_text, get_pdf_info
from core.generators.llm import LLMGenerator
from core.auth import AuthManager

st.set_page_config(page_title="Entrenamiento Oficial | ICFES Sim", page_icon="📖", layout="wide")

if not AuthManager.check_auth():
    st.warning("Por favor inicia sesión.")
    st.stop()

load_css()
render_custom_sidebar()
render_header(title="Entrenamiento Oficial (Guías) 📖", subtitle="Aprende directamente de los marcos de referencia del ICFES")

st.markdown("""
<div class='icfes-card'>
    <h3 class='icfes-header'>Actualiza la Inteligencia del Simulador</h3>
    <p>Sube las Guías de Orientación oficiales del ICFES (PDF) para generar preguntas con un nivel de fidelidad insuperable.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Subir Guía Oficial (PDF)", type=["pdf"])

if uploaded_file:
    info = get_pdf_info(uploaded_file)
    st.success(f"📄 Documento detectado: {uploaded_file.name} ({info['pages']} páginas)")
    
    with st.expander("⚙️ Configuración de Generación"):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("Materia a extraer", ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"])
            num_q = st.slider("Preguntas a generar", 1, 15, 5)
        with col2:
            ai_provider = st.selectbox("Proveedor de IA", ["Gemini", "Groq", "Mistral"])
            difficulty = st.select_slider("Dificultad", options=["Básico", "Intermedio", "Avanzado"], value="Intermedio")
            diff_val = {"Básico": 1, "Intermedio": 2, "Avanzado": 3}[difficulty]
            
            default_key = ""
            if ai_provider == "Gemini": default_key = os.getenv("GEMINI_API_KEY", "")
            elif ai_provider == "Groq": default_key = os.getenv("GROQ_API_KEY", "")
            else: default_key = os.getenv("MISTRAL_API_KEY", "")
            
            api_key = st.text_input(f"{ai_provider} API Key", value=default_key, type="password")

    if st.button("🚀 Procesar Guía y Generar Preguntas", type="primary", use_container_width=True):
        if not api_key:
            st.error("🔑 Falta la API Key.")
        else:
            with st.spinner("Leyendo guía oficial y diseñando preguntas estilo ICFES 2026..."):
                # Reset pointer to start of file for re-reading if necessary
                uploaded_file.seek(0)
                text_context = get_pdf_text(uploaded_file)
                
                if len(text_context) < 100:
                    st.error("No se pudo extraer suficiente texto del PDF. Asegúrate de que no sea solo una imagen.")
                else:
                    # Usamos el generador optimizado
                    # Limitamos el contexto para no saturar la API, tomando una muestra representativa o permitiendo que la IA analice
                    # Para este MVP, tomamos los primeros 25000 chars (aprox 10-15 paginas densas)
                    prog_placeholder = st.empty()
            with st.spinner("La IA está procesando la guía oficial..."):
                gen = LLMGenerator(provider=ai_provider, api_key=api_key)
                
                def update_prog(current, total):
                    prog_placeholder.progress(current / total, text=f"📥 Procesando guía: {current}/{total} preguntas...")

                questions = gen.generate_from_text(text_context, num_q=num_q, subject=subject, difficulty=diff_val, progress_callback=update_prog)
                prog_placeholder.empty()
    
                if questions:
                    db = SessionLocal()
                    saved = 0
                    seen_hashes = set()
                    for q_data in questions:
                        q_hash = hashlib.md5((q_data['stem'] + q_data['correct_key']).encode()).hexdigest()
                        if q_hash not in seen_hashes:
                            if not db.query(Question).filter_by(hash_norm=q_hash).first():
                                new_q = Question(
                                    subject=q_data['subject'],
                                    competency=q_data.get('competency', 'General'),
                                    topic=q_data['topic'],
                                    stem=q_data['stem'],
                                    options_json=q_data['options'],
                                    correct_key=q_data['correct_key'],
                                    rationale=q_data['rationale'],
                                    difficulty=diff_val,
                                    hash_norm=q_hash
                                )
                                db.add(new_q)
                                saved += 1
                                seen_hashes.add(q_hash)
                    try:
                        db.commit()
                        st.success(f"🎯 ¡Éxito! Se han creado {saved} preguntas de alta fidelidad basadas en la guía oficial.")
                        st.balloons()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error al guardar datos: {e}")
                    finally:
                        db.close()
                else:
                    st.error("La IA no pudo procesar la guía. Intenta de nuevo.")
