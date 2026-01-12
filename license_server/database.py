import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection string (from environment)
DATABASE_URL = os.getenv("PLANETSCALE_URL") or os.getenv("DATABASE_URL")

# Fallback for local testing
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local_test.db"
    connect_args = {}
else:
    DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")
    
    # Keep as PostgreSQL (CockroachDB is PostgreSQL-compatible)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    elif DATABASE_URL.startswith("cockroachdb+psycopg2://"):
        DATABASE_URL = DATABASE_URL.replace("cockroachdb+psycopg2://", "postgresql://", 1)
    
    # Ensure sslmode=require for CockroachDB
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        if "?" not in DATABASE_URL:
            DATABASE_URL += "?sslmode=require"
        elif "sslmode" not in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
    
    connect_args = {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=30,
    echo=False
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String(64), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    password = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), nullable=False)
    stripe_payment_intent = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    actor_id = Column(String(64), nullable=True)
    target_id = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
