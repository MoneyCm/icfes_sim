import psycopg2

# Credenciales DIAN (conocidas como funcionales)
dian_url = "postgresql://postgres.ejvpdzgnkstkljgwktfj:27UmC7ZGqh9t.bL@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

print("🔍 Probando conexión DIAN (Control)...")
try:
    conn = psycopg2.connect(dian_url)
    print("✅ ¡Conexión DIAN exitosa! La contraseña es correcta.")
    conn.close()
except Exception as e:
    print(f"❌ Error DIAN: {e}")
