import streamlit as st
import sys
import os

# Adaptación para navegación de páginas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Question
from ui_utils import load_css, render_header, render_custom_sidebar
from core.generators.llm import LLMGenerator
from core.auth import AuthManager
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Generador IA | ICFES Sim", page_icon="🤖", layout="wide")

if not AuthManager.check_auth():
    st.warning("Por favor inicia sesión para usar la IA.")
    st.stop()

load_css()
render_custom_sidebar()
render_header(title="Generador de Preguntas IA 🤖", subtitle="Crea retos personalizados para tu ICFES")

with st.container():
    st.markdown("""
    <div class='icfes-card'>
        <h3 class='icfes-header'>Configuración del Reto</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.selectbox("Materia", ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"])
        num_q = st.slider("Número de preguntas", 1, 50, 10)
    
    with col2:
        ai_provider = st.selectbox("Proveedor de IA", ["Gemini", "Groq", "Mistral"])
        difficulty = st.select_slider("Nivel de dificultad", options=["Básico", "Intermedio", "Avanzado"], value="Intermedio")
        diff_val = {"Básico": 1, "Intermedio": 2, "Avanzado": 3}[difficulty]

    with col3:
        # Intentar obtener API Key de .env si no está en session_state
        default_key = ""
        if ai_provider == "Gemini":
            default_key = os.getenv("GEMINI_API_KEY", "")
        elif ai_provider == "Groq":
            default_key = os.getenv("GROQ_API_KEY", "")
        else:
            default_key = os.getenv("MISTRAL_API_KEY", "")
            
        api_key = st.text_input(f"{ai_provider} API Key", value=default_key, type="password")

    st.markdown("#### 📄 Modalidad de Generación")
    gen_mode = st.radio("¿Cómo quieres generar las preguntas?", ["Usar un texto de referencia", "Generación libre (Conocimiento de la IA)"], horizontal=True)

    source_text = ""
    if gen_mode == "Usar un texto de referencia":
        source_text = st.text_area("Pega aquí el texto, lectura o ejercicio del cual quieres generar preguntas:", height=150)
    else:
        st.info(f"💡 {ai_provider} generará preguntas basadas en los estándares oficiales del ICFES.")

    if st.button("✨ Generar con IA", type="primary", use_container_width=True):
        if not api_key:
            st.error(f"🔑 Falta la API Key de {ai_provider}.")
        elif gen_mode == "Usar un texto de referencia" and len(source_text) < 50:
            st.warning("📋 El texto es muy corto para generar preguntas de calidad.")
        else:
            prog_placeholder = st.empty()
            with st.spinner(f"{ai_provider} está creando tus preguntas..."):
                gen = LLMGenerator(provider=ai_provider, api_key=api_key)
                context_to_use = source_text if gen_mode == "Usar un texto de referencia" else None
                
                def update_prog(current, total):
                    perc = int((current / total) * 100)
                    prog_placeholder.progress(current / total, text=f"📥 Generando: {current}/{total} preguntas...")

                questions = gen.generate_from_text(context_to_use, num_q=num_q, subject=subject, difficulty=diff_val, progress_callback=update_prog)
                prog_placeholder.empty()
                if questions:
                    db = SessionLocal()
                    saved_count = 0
                    seen_hashes = set()
                    
                    for q_data in questions:
                        # Crear hash para evitar duplicados
                        import hashlib
                        q_hash = hashlib.md5((q_data['stem'] + q_data['correct_key']).encode()).hexdigest()
                        
                        # Evitar duplicados en el mismo lote y en la base de datos
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
                                saved_count += 1
                                seen_hashes.add(q_hash)
                    
                    try:
                        db.commit()
                        st.success(f"✅ ¡Se han generado {len(questions)} preguntas y guardado {saved_count} nuevas en el banco!")
                        st.session_state["last_gen_questions"] = questions
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error de base de datos: {e}")
                    finally:
                        db.close()
                else:
                    st.error("Hubo un problema al generar las preguntas.")

    st.markdown("</div>", unsafe_allow_html=True)

# Mostrar resultados
if "last_gen_questions" in st.session_state:
    st.divider()
    for i, q in enumerate(st.session_state["last_gen_questions"]):
        with st.expander(f"Pregunta {i+1}: {q['topic']}"):
            st.markdown(f"**{q['stem']}**")
            for key, val in q['options'].items():
                st.write(f"**{key})** {val}")
            st.markdown(f"**Correcta:** :green[{q['correct_key']}]")
            st.info(f"💡 {q['rationale']}")
