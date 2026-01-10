"""
Shadow Watch FastAPI Integration Example

Shows how to integrate Shadow Watch into a FastAPI application
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import add_shadow_watch
from shadowwatch.models import Base
import os

# Initialize FastAPI app
app = FastAPI(title="Shadow Watch Example")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/shadowwatch_demo")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=DATABASE_URL,
    license_key=os.getenv("SHADOWWATCH_LICENSE", "SW-TRIAL-0001-2026-A1B2")
)


# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Shadow Watch tables created")


# Add Shadow Watch middleware (automatic tracking!)
add_shadow_watch(
    app,
    shadow_watch=sw,
    user_id_getter=lambda req: getattr(req.state, 'user_id', 1)  # Get from your auth
)


# Example: View stock (automatically tracked by middleware)
@app.get("/stocks/{symbol}")
async def view_stock(symbol: str, request: Request):
    """User views a stock - Shadow Watch tracks automatically via middleware"""
    
    # Set user ID (normally from auth middleware)
    request.state.user_id = 1
    
    # Just return your data - tracking happens automatically!
    return {
        "symbol": symbol,
        "price": 150.25,
        "change": "+2.5%"
    }


# Example: Get user's behavioral profile
@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    """Get user's Shadow Watch profile"""
    
    profile = await sw.get_profile(user_id)
    return profile


# Example: Verify login trust score
@app.post("/auth/verify")
async def verify_login(user_id: int, ip: str, user_agent: str):
    """Check if login is trustworthy"""
    
    trust_result = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": ip,
            "user_agent": user_agent,
            "library_fingerprint": ""  # Would come from client cache
        }
    )
    
    if trust_result["action"] == "block":
        raise HTTPException(status_code=403, detail="Suspicious login attempt")
    
    return trust_result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# Example: Get user's behavioral profile
@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    """Get user's Shadow Watch profile"""
    
    profile = await sw.get_profile(user_id)
    return profile


# Example: Verify login trust score
@app.post("/auth/verify")
async def verify_login(user_id: int, ip: str, user_agent: str):
    """Check if login is trustworthy"""
    
    trust_result = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": ip,
            "user_agent": user_agent,
            "library_fingerprint": ""  # Would come from client cache
        }
    )
    
    if trust_result["action"] == "block":
        raise HTTPException(status_code=403, detail="Suspicious login attempt")
    
    return trust_result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
