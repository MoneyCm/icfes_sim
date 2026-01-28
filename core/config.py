import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env si existe
load_dotenv()

def get_api_key(provider="Gemini"):
    """
    Obtiene la API Key desde las variables de entorno o Streamlit Secrets.
    Mikey v1.2
    """
    key_name = f"{provider.upper()}_API_KEY"
    
    # Intentar obtener de variables de entorno (.env o sistema)
    api_key = os.getenv(key_name)
    
    # Fallback para Streamlit (secrets.toml)
    if not api_key:
        import streamlit as st
        try:
            api_key = st.secrets.get(key_name)
        except:
            pass
            
    return api_key or ""
