import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    question_id = Column(String(36), primary_key=True)
    subject = Column(String)
    difficulty = Column(Integer)
    created_at = Column(DateTime)

def trim_to_target():
    db = SessionLocal()
    target = 250
    subjects = ["Ciencias Naturales", "Inglés", "Sociales y Ciudadanas", "Matemáticas", "Lectura Crítica"]
    
    total_deleted = 0
    for sub in subjects:
        for diff in [1, 2, 3]:
            qs = db.query(Question).filter(
                Question.subject == sub,
                Question.difficulty == diff
            ).order_by(Question.created_at.desc()).all()
            
            if len(qs) > target:
                to_delete = qs[target:]
                for q in to_delete:
                    db.delete(q)
                total_deleted += len(to_delete)
                print(f"Trimming {sub} (Level {diff}): Removed {len(to_delete)} questions.")
    
    db.commit()
    db.close()
    print(f"Final Cleanup Complete. Total trimmed: {total_deleted}")

if __name__ == "__main__":
    trim_to_target()
