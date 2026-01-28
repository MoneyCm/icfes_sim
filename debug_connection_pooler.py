import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Parámetros extraídos de la URL del usuario
host = "aws-1-us-east-2.pooler.supabase.com"
user = "postgres.nhuqlrfslvmhbythszeu"
password = "27UmC7ZGqh9t.bL"
dbname = "postgres"

test_ports = [6543, 5432]

print("🔬 DIAGNÓSTICO DE CONEXIÓN ICFES (Pooler)")
for port in test_ports:
    print(f"\n--- Probando Puerto {port} ---")
    try:
        # Intento con parámetros explícitos (más robusto)
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=port,
            connect_timeout=10
        )
        print(f"✅ ¡ÉXITO! Conexión lograda en puerto {port}")
        conn.close()
        break
    except Exception as e:
        print(f"❌ Fallo en puerto {port}: {e}")

print("\n--- Intento con URL Directa (DNS) ---")
try:
    direct_url = f"postgresql://postgres:{password}@db.nhuqlrfslvmhbythszeu.supabase.co:5432/postgres"
    conn = psycopg2.connect(direct_url)
    print("✅ ¡ÉXITO! Conexión Directa lograda.")
    conn.close()
except Exception as e:
    print(f"❌ Fallo Directo: {e}")
