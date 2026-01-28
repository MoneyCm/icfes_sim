import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Parámetros conocidos
host_pooler = "aws-1-us-east-2.pooler.supabase.com"
passw = "27UmC7ZGqh9t.bL"
project_ref = "nhuqlrfslvmhbythszeu"

tests = [
    # Intento con usuario plano (a veces el pooler base lo prefiere)
    {"u": "postgres", "h": host_pooler, "p": 6543},
    {"u": "postgres", "h": host_pooler, "p": 5432},
]

print("🧪 ESCANEO DE VARIACIONES")
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
