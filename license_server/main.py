from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Import Redis-based store (works with Vercel KV or local Redis)
from kv_store import LicenseStore

app = FastAPI(title="Shadow Watch License Server")

# No database initialization needed (Redis/KV is managed externally)

# Request/Response models
class VerifyRequest(BaseModel):
    key: str

class ReportRequest(BaseModel):
    license_key: str
    events_count: int
    timestamp: str


@app.on_event("startup")
async def startup():
    """Startup message"""
    print("✅ Shadow Watch License Server started")
    print("💾 Storage: Redis/Vercel KV (serverless-compatible)")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.0.0",
        "storage": "Redis/Vercel KV"
    }


@app.post("/verify")
async def verify_license(req: VerifyRequest):
    """
    Verify if license key is valid and not expired
    
    Returns license details if valid, 403 if invalid/expired
    """
    # Get from Redis/KV
    license_data = LicenseStore.get_license(req.key)
    
    if not license_data:
        raise HTTPException(status_code=403, detail="License key not found")
    
    # Check if expired
    try:
        expires_at = datetime.fromisoformat(license_data["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=403, detail="License key expired")
    except (KeyError, ValueError):
        raise HTTPException(status_code=403, detail="Invalid license data")
    
    # Check if active
    if not license_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="License key deactivated")
    
    return {
        "valid": True,
        "tier": license_data["tier"],
        "max_events": license_data["max_events"],
        "customer": license_data.get("customer_name", "Trial User"),
        "expires_at": license_data["expires_at"]
    }


@app.post("/report")
async def report_usage(req: ReportRequest):
    """
    Receive usage report from customer's Shadow Watch instance
    
    Stores event count for billing/monitoring
    """
    # Verify license exists
    license_data = LicenseStore.get_license(req.license_key)
    if not license_data:
        raise HTTPException(status_code=404, detail="License key not found")
    
    # Store usage report
    LicenseStore.report_usage(
        req.license_key,
        req.events_count,
        req.timestamp
    )
    
    return {"status": "received"}


@app.get("/stats")
async def get_stats():
    """
    Admin endpoint: Get usage statistics
    
    Returns total customers, licenses, and events
    """
    licenses = LicenseStore.list_all_licenses()
    
    # Count active licenses
    active_licenses = [l for l in licenses if l.get("is_active", True)]
    
    # Count active trials (not expired)
    active_trials = [
        l for l in active_licenses 
        if l.get("tier") == "trial" and 
        datetime.fromisoformat(l["expires_at"]) > datetime.utcnow()
    ]
    
    # Total events tracked
    total_events = sum(
        LicenseStore.get_total_events(l["license_key"]) 
        for l in licenses
    )
    
    return {
        "total_licenses": len(active_licenses),
        "active_trials": len(active_trials),
        "total_events_tracked": total_events
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Request/Response models
class VerifyRequest(BaseModel):
    key: str

class ReportRequest(BaseModel):
    license_key: str
    events_count: int
    timestamp: str

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                tier TEXT NOT NULL,
                max_events INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS usage_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                events_count INTEGER NOT NULL,
                reported_at TEXT NOT NULL,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key)
            );
        """)
        conn.commit()

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("✅ License server started")
    print(f"📊 Database: {DB_PATH}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.0.0"
    }

@app.post("/verify")
async def verify_license(req: VerifyRequest):
    """
    Verify if license key is valid and not expired
    
    Returns license details if valid, 403 if invalid/expired
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tier, max_events, customer_name, expires_at, is_active
            FROM licenses 
            WHERE license_key = ?
        """, (req.key,))
        
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=403, detail="License key not found")
        
        # Check if expired
        expires_at = datetime.fromisoformat(row['expires_at'])
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=403, detail="License key expired")
        
        # Check if active
        if not row['is_active']:
            raise HTTPException(status_code=403, detail="License key deactivated")
        
        return {
            "valid": True,
            "tier": row['tier'],
            "max_events": row['max_events'],
            "customer": row['customer_name'] or "Trial User",
            "expires_at": row['expires_at']
        }

@app.post("/report")
async def report_usage(req: ReportRequest):
    """
    Receive usage report from customer's Shadow Watch instance
    
    Stores event count for billing/monitoring
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify license exists
        cursor.execute("SELECT 1 FROM licenses WHERE license_key = ?", (req.license_key,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="License key not found")
        
        # Insert usage report
        cursor.execute("""
            INSERT INTO usage_reports (license_key, events_count, reported_at)
            VALUES (?, ?, ?)
        """, (req.license_key, req.events_count, req.timestamp))
        
        conn.commit()
    
    return {"status": "received"}

@app.get("/stats")
async def get_stats():
    """
    Admin endpoint: Get usage statistics
    
    Returns total customers, licenses, and events
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total licenses
        cursor.execute("SELECT COUNT(*) as count FROM licenses WHERE is_active = 1")
        total_licenses = cursor.fetchone()['count']
        
        # Total events reported
        cursor.execute("SELECT SUM(events_count) as total FROM usage_reports")
        total_events = cursor.fetchone()['total'] or 0
        
        # Active trials
        cursor.execute("""
            SELECT COUNT(*) as count FROM licenses 
            WHERE tier = 'trial' AND is_active = 1 AND expires_at > ?
        """, (datetime.utcnow().isoformat(),))
        active_trials = cursor.fetchone()['count']
        
        return {
            "total_licenses": total_licenses,
            "active_trials": active_trials,
            "total_events_tracked": total_events
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
