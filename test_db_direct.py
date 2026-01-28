import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")

print(f"🔍 Probando conexión a: {url.split('@')[-1]}")
try:
    conn = psycopg2.connect(url)
    print("✅ ¡Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"❌ Error detallado: {e}")
