import psycopg2

# DIAN (Functional)
dian_user = "postgres.ejvpdzgnkstkljgwktfj"
dian_host = "aws-1-us-east-1.pooler.supabase.com"
password = "27UmC7ZGqh9t.bL"

# ICFES (Failing)
icfes_user = "postgres.nhuqlrfslvmhbythszeu"
icfes_host = "aws-1-us-east-2.pooler.supabase.com"

print("🔍 TEST DE COMPARACIÓN")
print(f"DIAN User: {dian_user}")
print(f"ICFES User: {icfes_user}")

def try_conn(u, h, p=6543):
    try:
        conn = psycopg2.connect(host=h, user=u, password=password, dbname="postgres", port=p)
        print(f"✅ OK: {u} @ {h}:{p}")
        conn.close()
    except Exception as e:
        print(f"❌ FALLO: {u} @ {h}:{p} -> {e}")

try_conn(dian_user, dian_host)
try_conn(icfes_user, icfes_host)
