
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection string (from Vercel env vars)
DATABASE_URL = os.getenv("PLANETSCALE_URL") or os.getenv("DATABASE_URL")

# Fallback for local testing if env var not set (SQLite)
if not DATABASE_URL:
    print("⚠️ DATABASE_URL not set. Using local SQLite for testing.")
    DATABASE_URL = "sqlite:///./local_test.db"
else:
    # Use direct URL from environment
    DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")
    
    # Simple swap for SQLAlchemy 1.4+
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print("📡 Database engine initialized")
    
connect_args = {}

# Handle SSL for CockroachDB (PostgreSQL) or PlanetScale (MySQL)
if "mysql" in DATABASE_URL:
    connect_args = {"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}}
elif "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # CockroachDB often puts sslmode in the URL itself, but we can enforce it here if needed
    # Usually empty is fine if the URL has ?sslmode=verify-full
    pass

def get_engine():
    """Lazily create engine to prevent import-time crashes"""
    return create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_recycle=3600,
        pool_pre_ping=True
    )

def SessionLocal():
    """Factory for database sessions"""
    engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()

Base = declarative_base()

class User(Base):
    """
    Customer accounts (from dashboard signups)
    
    Stores identity and billing relationship.
    Does NOT store behavioral data (that's in the client's DB).
    """
    __tablename__ = "users"
    
    id = Column(String(64), primary_key=True)  # Auth0 ID or internal UUID
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    password = Column(String(255), nullable=True) # Optional for guest users
    
    # Billing info
    stripe_customer_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="free")  # free, pro, enterprise
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(Base):
    """
    Payment history log
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), nullable=False)  # succeeded, failed, pending
    stripe_payment_intent = Column(String(255), unique=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    """
    Admin actions and security audit trail
    
    Logs:
    - License creation/revocation
    - User bans
    - System configuration changes
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)  # e.g., "license.created", "user.banned"
    actor_id = Column(String(64), nullable=True)  # Who did it (Admin ID or System)
    target_id = Column(String(64), nullable=True) # Who was affected (User ID or License Key)
    details = Column(Text, nullable=True)         # JSON blob or text description
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Create tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
