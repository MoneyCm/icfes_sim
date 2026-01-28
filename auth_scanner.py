import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Parámetros conocidos
host_pooler = "aws-1-us-east-2.pooler.supabase.com"
host_direct_ipv4_pooler = "3.148.140.216" # Usando la IP del pooler para test
passw = "27UmC7ZGqh9t.bL"
project_ref = "nhuqlrfslvmhbythszeu"

tests = [
    # Puerto 6543 (Transaction Pooler)
    {"u": f"postgres.{project_ref}", "h": host_pooler, "p": 6543},
    # Puerto 5432 (Session Pooler)
    {"u": f"postgres.{project_ref}", "h": host_pooler, "p": 5432},
]

print("🧪 ESCANEO DE AUTENTICACIÓN")
for t in tests:
    print(f"\nProbando: {t['u']} @ {t['h']}:{t['p']}")
    try:
        conn = psycopg2.connect(
            host=t['h'],
            user=t['u'],
            password=passw,
            dbname="postgres",
            port=t['p'],
            connect_timeout=5
        )
        print("✅ ¡ÉXITO!")
        conn.close()
    except Exception as e:
        print(f"❌ FALLO: {e}")
