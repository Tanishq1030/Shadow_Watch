import os
import re
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode

# Database connection string (from Vercel env vars)
RAW_URL = os.getenv("PLANETSCALE_URL") or os.getenv("DATABASE_URL")

def get_connection_url(url: str) -> str:
    if not url:
        return "sqlite:///./local_test.db"
    
    url = url.strip().strip('"').strip("'")
    
    # Handle CockroachDB / Postgres
    if url.startswith("postgres"):
        # Ensure postgresql://
        if not url.startswith("postgresql://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        # Parse and ensure sslmode
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params['sslmode'] = ['verify-full']
        
        new_query = urlencode(params, doseq=True)
        url = parsed._replace(query=new_query).geturl()
        
    return url

DATABASE_URL = get_connection_url(RAW_URL)

connect_args = {}
if "mysql" in DATABASE_URL:
    connect_args = {"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_recycle=3600,
    pool_pre_ping=True
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
