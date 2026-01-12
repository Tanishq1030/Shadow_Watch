import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection string (from Supabase environment variable)
# Use pooler URL for better performance with serverless
DATABASE_URL = os.getenv("POSTGRES_POOLER_URL") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No Supabase database URL found (tried POSTGRES_POOLER_URL, POSTGRES_URL, DATABASE_URL)")

# Clean up the URL
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")

# Keep as PostgreSQL (Supabase uses PostgreSQL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}

try:
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
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Database engine creation failed: {e}")
    # Create engine anyway to prevent None errors, but it will fail on first use
    from sqlalchemy import create_engine as ce
    from sqlalchemy.pool import NullPool
    engine = ce("sqlite:///:memory:", poolclass=NullPool)  # Fallback to prevent crash
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
