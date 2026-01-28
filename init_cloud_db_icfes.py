import sys
import os

# Asegurar que el script encuentre los módulos core y db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from db.session import init_db
import sqlalchemy

print("🚀 Iniciando conexión con Supabase...")
try:
    init_db()
    print("✅ ¡Tablas creadas exitosamente en la nube!")
except Exception as e:
    print(f"❌ Error al inicializar la base de datos: {e}")
