from __future__ import annotations
import datetime
import uuid
import sys
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="student")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    subjects: Mapped[List["UserSubject"]] = relationship("UserSubject", back_populates="user", cascade="all, delete-orphan")
    stats: Mapped[Optional["UserStats"]] = relationship("UserStats", back_populates="user", cascade="all, delete-orphan")
    attempts: Mapped[List["Attempt"]] = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[List["Achievement"]] = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")

class UserSubject(Base):
    """Reemplaza a UserOPEC para el ICFES. Mikey v1.0"""
    __tablename__ = "user_subjects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    subject_name: Mapped[str] = mapped_column(String) # Matemáticas, Lectura Crítica, etc.
    target_score: Mapped[int] = mapped_column(Integer, default=100) # Meta de puntaje por área
    is_priority: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped[Optional["User"]] = relationship("User", back_populates="subjects")

class Question(Base):
    __tablename__ = "questions"
    question_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject: Mapped[str] = mapped_column(String) # Área del ICFES
    competency: Mapped[str] = mapped_column(String) # Competencia evaluada
    topic: Mapped[str] = mapped_column(String) # Tema específico
    difficulty: Mapped[int] = mapped_column(Integer)
    stem: Mapped[str] = mapped_column(Text)
    options_json: Mapped[dict] = mapped_column(JSON)
    correct_key: Mapped[Optional[str]] = mapped_column(String)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    hash_norm: Mapped[str] = mapped_column(String, unique=True)
    
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    global_hits: Mapped[int] = mapped_column(Integer, default=0)
    global_misses: Mapped[int] = mapped_column(Integer, default=0)

    attempts: Mapped[List["Attempt"]] = relationship("Attempt", back_populates="question")

class Attempt(Base):
    __tablename__ = "attempts"
    attempt_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.question_id"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    chosen_key: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    time_sec: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    question: Mapped["Question"] = relationship("Question", back_populates="attempts")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="attempts")

class UserStats(Base):
    __tablename__ = "user_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="stats")

class Achievement(Base):
    __tablename__ = "achievements"
    achievement_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    icon: Mapped[Optional[str]] = mapped_column(String)
    unlocked_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped[Optional["User"]] = relationship("User", back_populates="achievements")

class ExamStyle(Base):
    """Almacena el 'ADN Pedagógico' extraído de guías oficiales. Mikey"""
    __tablename__ = "exam_styles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True) # Ej: "Guía Matemáticas 2025"
    subject: Mapped[str] = mapped_column(String)
    style_dna: Mapped[str] = mapped_column(Text) # Instrucciones comprimidas de estilo
    is_official: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
