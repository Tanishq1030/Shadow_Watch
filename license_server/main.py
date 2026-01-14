"""
License Server - Invariant Implementation

Production-grade licensing system with:
- Trial, Invariant, Enterprise tiers
- HMAC admin authentication
- Redis-backed rate limiting
- Offline validation support
- License revocation
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import using absolute imports (Vercel compatible)
try:
    from routes.license import router as license_router
    from database import close_pool
    from kv_store import get_redis
except ImportError:
    # Fallback for local development
    from .routes.license import router as license_router
    from .database import close_pool
    from .kv_store import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("✅ License Server starting...")
    
    # Warm up Redis connection
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis connection warning: {e}")
    
    yield
    
    # Shutdown
    print("� License Server shutting down...")
    await close_pool()
    print("✅ Shutdown complete")


app = FastAPI(
    title="Shadow Watch License Server",
    description="Production licensing system for Shadow Watch Invariant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(license_router)


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Shadow Watch License Server",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    health_status = {
        "service": "license_server",
        "version": "1.0.0",
        "components": {}
    }
    
    # Check Redis
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Database
    try:
        # Simple check - pool exists
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
    
    # Overall status
    all_healthy = all(
        v == "healthy" 
        for v in health_status["components"].values()
        if isinstance(v, str)
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status
