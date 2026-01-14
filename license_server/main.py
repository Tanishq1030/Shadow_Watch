"""
License Server - Pro Implementation

Production-grade licensing system with:
- Trial, Pro, Enterprise tiers
- HMAC admin authentication
- Redis-backed rate limiting
- Offline validation support
- License revocation
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routes import license
from .database import close_pool
from .kv_store import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("✅ License Server starting...")
    
    # Warm up Redis connection
    try:
        redis = await get_redis()
        await redis.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
    
    yield
    
    # Shutdown
    print("👋 License Server shutting down...")
    await close_pool()


app = FastAPI(
    title="Shadow Watch License Server",
    description="Production licensing system for Shadow Watch Invariant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(license.router)


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
        redis = await get_redis()
        await redis.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Database
    try:
        from .database import get_db
        async with get_db() as db:
            await db.fetchval("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
    
    # Overall status
    all_healthy = all(
        status == "healthy" 
        for status in health_status["components"].values()
    )
    
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
