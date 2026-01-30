import streamlit as st
import sys
import os
import hashlib

# Adaptación para navegación de páginas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Question, ExamStyle
from ui_utils import load_css, render_header, render_custom_sidebar
from core.pdf_utils import get_pdf_text, get_pdf_info
from core.generators.llm import LLMGenerator
from core.auth import AuthManager
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Entrenamiento Oficial | ICFES Sim", page_icon="📖", layout="wide")

if not AuthManager.check_auth():
    st.warning("Por favor inicia sesión.")
    st.stop()

load_css()
render_custom_sidebar()
render_header(title="Entrenamiento Oficial y Base de Conocimiento 🧠", subtitle="Gestiona el ADN Pedagógico del ICFES")

# Obtener estilos guardados
db = SessionLocal()
saved_styles = db.query(ExamStyle).all()
style_options = {s.name: s.style_dna for s in saved_styles}
db.close()

# Tabs para organizar flujos
tab_gen, tab_dna, tab_ext = st.tabs(["✨ Generar Nuevas", "🧬 Extraer ADN de Estilo", "🔍 Extraer Preguntas (Literal)"])

# --- TAB 1: GENERACIÓN ---
with tab_gen:
    st.markdown("Crea preguntas nuevas imitando estilos oficiales guardados.")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Materia", ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"], key="gen_sub")
        style_name = st.selectbox("Estilo Base (Knowledge Base)", ["Generico (IA Pura)"] + list(style_options.keys()))
        num_q = st.slider("Cantidad", 1, 20, 5, key="gen_num")
    
    with col2:
        ai_provider = st.selectbox("Proveedor IA", ["Gemini", "Groq", "Mistral"], key="gen_prov")
        difficulty = st.select_slider("Dificultad", options=["Básico", "Intermedio", "Avanzado"], value="Intermedio", key="gen_diff")
        
        default_key = ""
        if ai_provider == "Gemini": default_key = os.getenv("GEMINI_API_KEY", "")
        elif ai_provider == "Groq": default_key = os.getenv("GROQ_API_KEY", "")
        else: default_key = os.getenv("MISTRAL_API_KEY", "")
        api_key = st.text_input("API Key", value=default_key, type="password", key="gen_key")

    if st.button("🚀 Generar Preguntas", type="primary", use_container_width=True):
        if not api_key:
            st.error("Falta API Key")
        else:
            with st.spinner("Generando..."):
                gen = LLMGenerator(provider=ai_provider, api_key=api_key)
                
                # Contexto: Estilo seleccionado
                context = style_options.get(style_name, None) if style_name != "Generico (IA Pura)" else None
                diff_val = {"Básico": 1, "Intermedio": 2, "Avanzado": 3}[difficulty]
                
                questions = gen.generate_from_text(context=context, num_q=num_q, subject=subject, difficulty=diff_val)
                
                if questions:
                    db = SessionLocal()
                    saved = 0
                    for q in questions:
                        q_hash = hashlib.md5((q['stem'] + q['correct_key']).encode()).hexdigest()
                        if not db.query(Question).filter_by(hash_norm=q_hash).first():
                            new_q = Question(
                                subject=subject,
                                competency=q.get('competency', 'General'),
                                topic=q.get('topic', 'General'),
                                stem=q.get('stem'),
                                options_json=q.get('options'),
                                correct_key=q.get('correct_key'),
                                rationale=q.get('rationale', ''),
                                difficulty=diff_val,
                                is_verified=True if context else False, # Si usa estilo oficial, es semi-verificada/alta fidelidad
                                hash_norm=q_hash
                            )
                            db.add(new_q)
                            saved += 1
                    try:
                        db.commit()
                        st.success(f"¡Éxito! {saved} preguntas generadas.")
                        st.balloons()
                    except:
                        db.rollback()
                    finally:
                        db.close()

# --- TAB 2: EXTRAER ADN (ESTILO) ---
with tab_dna:
    st.markdown("Sube una guía PDF para que la IA aprenda su estructura y cree un 'Estilo'.")
    file_dna = st.file_uploader("Subir Guía Oficial", type=["pdf"], key="dna_file")
    
    if file_dna:
        dna_subject = st.selectbox("Materia del Documento", ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"], key="dna_sub")
        dna_name = st.text_input("Nombre para este Estilo (Ej: Guía 2025)", key="dna_name")
        
        if st.button("🧬 Analizar y Guardar ADN"):
            text = get_pdf_text(file_dna)
            with st.spinner("Analizando patrones pedagógicos..."):
                # Usamos una instancia temporal con la key por defecto o pedimos una
                # Por simplicidad reusamos variables de entorno si existen, o pedimos en UI
                # Asumimos que el usuario ya configuró keys en .env o en la otra tab (esto es una simplificación UX)
                prov = "Gemini" # Default rápido
                k = os.getenv("GEMINI_API_KEY")
                if k:
                    gen = LLMGenerator(provider=prov, api_key=k)
                    dna = gen.analyze_style_dna(text, subject=dna_subject)
                    
                    if dna:
                        st.info("ADN Extraído:")
                        st.code(dna)
                        
                        if dna_name:
                            db = SessionLocal()
                            if not db.query(ExamStyle).filter_by(name=dna_name).first():
                                new_style = ExamStyle(name=dna_name, subject=dna_subject, style_dna=dna)
                                db.add(new_style)
                                db.commit()
                                st.success("¡Estilo guardado en Base de Conocimiento!")
                                st.rerun()
                            else:
                                st.warning("Ya existe un estilo con ese nombre.")
                            db.close()
                else:
                    st.error("Configura tu GEMINI_API_KEY en .env para esta función rápida.")

# --- TAB 3: EXTRAER LITERAL ---
with tab_ext:
    st.markdown("Extrae preguntas tal cual aparecen en el PDF.")
    uploaded_file = st.file_uploader("Subir Cuadernillo", type=["pdf"], key="ext_file")
    
    if uploaded_file:
        # Reutilizamos lógica anterior pero simplificada
        ext_subject = st.selectbox("Materia", ["Matemáticas", "Lectura Crítica", "Ciencias Naturales", "Sociales y Ciudadanas", "Inglés"], key="ext_sub")
        ext_prov = st.selectbox("Proveedor", ["Gemini", "Groq", "Mistral"], key="ext_prov")
        ext_key = st.text_input("API Key", type="password", key="ext_key")
        
        if st.button("🔍 Extraer Preguntas"):
             if ext_key:
                text_context = get_pdf_text(uploaded_file)
                gen = LLMGenerator(provider=ext_prov, api_key=ext_key)
                qs = gen.extract_from_booklet(text_context, subject=ext_subject)
                # Guardado... (similar a generación)
                if qs:
                    db = SessionLocal()
                    saved = 0
                    for q in qs:
                        q_hash = hashlib.md5((q['stem'] + q['correct_key']).encode()).hexdigest()
                        if not db.query(Question).filter_by(hash_norm=q_hash).first():
                            new_q = Question(
                                subject=ext_subject,
                                competency=q.get('competency', 'General'),
                                topic=q.get('topic', 'General'),
                                stem=q.get('stem'),
                                options_json=q.get('options'),
                                correct_key=q.get('correct_key'),
                                rationale=q.get('rationale', ''),
                                difficulty=2,
                                is_verified=True,
                                hash_norm=q_hash
                            )
                            db.add(new_q)
                            saved += 1
                    db.commit()
                    st.success(f"Guardadas {saved} preguntas oficiales.")
                    db.close()
