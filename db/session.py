import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Prioridad: Variable de entorno (Nube) -> SQLite local (Desarrollo)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./icfes_sim.db")

# Ajuste para PostgreSQL en modo pooler (Supabase)
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)
