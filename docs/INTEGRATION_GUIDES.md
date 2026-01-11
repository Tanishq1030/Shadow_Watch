# Shadow Watch - Integration Guides

Step-by-step guides for integrating Shadow Watch into popular Python frameworks.

---

## Table of Contents

- [FastAPI Integration](#fastapi-integration)
- [Django Integration](#django-integration)
- [Flask Integration](#flask-integration)
- [General Python Application](#general-python-application)

---

## FastAPI Integration

### Basic Setup (5 Minutes)

**1. Install Shadow Watch:**

```bash
pip install shadowwatch[fastapi]
```

**2. Initialize in your app:**

```python
# main.py
from fastapi import FastAPI, Request, Depends
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware
import os

app = FastAPI()

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE_KEY"),
    redis_url=os.getenv("REDIS_URL")  # Production only
)

# Add middleware for automatic tracking
app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    extract_user_id=lambda request: getattr(request.state, 'user_id', None),
    extract_entity_id=lambda request: request.path_params.get("symbol"),
    extract_action=lambda request: request.method.lower()
)
```

**3. Add authentication middleware:**

```python
from fastapi import HTTPException
import jwt

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Extract JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if token:
        try:
            # Decode JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.state.user_id = payload.get("user_id")
        except jwt.InvalidTokenError:
            pass
    
    response = await call_next(request)
    return response
```

**4. Your routes now auto-track:**

```python
@app.get("/stocks/{symbol}")
async def get_stock(symbol: str):
    # Shadow Watch automatically tracks:
    # - user_id (from request.state.user_id)
    # - entity_id (symbol)
    # - action ("get")
    
    return {"symbol": symbol, "price": 185.20}
```

---

### Advanced: Custom Tracking

**For routes that need custom tracking logic:**

```python
from fastapi import Depends

def get_shadowwatch():
    return sw

@app.post("/trades")
async def create_trade(
    trade_data: TradeData,
    request: Request,
    sw: ShadowWatch = Depends(get_shadowwatch)
):
    # Custom tracking with metadata
    await sw.track(
        user_id=request.state.user_id,
        entity_id=trade_data.symbol,
        action="trade",
        metadata={
            "side": trade_data.side,
            "quantity": trade_data.quantity,
            "price": trade_data.price,
            "total": trade_data.quantity * trade_data.price
        }
    )
    
    # Execute trade
    result = execute_trade(trade_data)
    return result
```

---

### Login Verification Integration

```python
@app.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    # Verify username/password
    user = authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check behavioral trust score
    trust = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.cookies.get("device_fp"),
            "library_fingerprint": credentials.fingerprint  # From client cache
        }
    )
    
    # Handle based on trust score
    if trust["action"] == "allow":
        # Generate JWT token
        token = generate_jwt(user.id)
        return {"success": True, "token": token}
    
    elif trust["action"] == "require_mfa":
        # Request 2FA
        send_mfa_code(user.id)
        return {
            "success": False,
            "require_mfa": True,
            "message": "Please enter the code sent to your phone"
        }
    
    else:  # "block"
        # Deny login + alert user
        send_security_alert(user.id, request.client.host)
        raise HTTPException(
            status_code=403,
            detail="Suspicious login attempt detected"
        )
```

---

## Django Integration

### Basic Setup (10 Minutes)

**1. Install Shadow Watch:**

```bash
pip install shadowwatch
```

**2. Add to Django settings:**

```python
# settings.py
import os

SHADOWWATCH_CONFIG = {
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'LICENSE_KEY': os.getenv('SHADOWWATCH_LICENSE_KEY'),
    'REDIS_URL': os.getenv('REDIS_URL'),  # Production only
}
```

**3. Create Shadow Watch instance:**

```python
# shadowwatch_instance.py
from shadowwatch import ShadowWatch
from django.conf import settings

sw = ShadowWatch(
    database_url=settings.SHADOWWATCH_CONFIG['DATABASE_URL'],
    license_key=settings.SHADOWWATCH_CONFIG['LICENSE_KEY'],
    redis_url=settings.SHADOWWATCH_CONFIG.get('REDIS_URL')
)
```

**4. Create Django middleware:**

```python
# middleware/shadowwatch_middleware.py
from shadowwatch_instance import sw
import asyncio

class ShadowWatchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Track activity if user is authenticated
        if request.user.is_authenticated:
            # Extract entity ID from URL
            entity_id = self._extract_entity_id(request)
            
            if entity_id:
                # Track asynchronously (don't block request)
                asyncio.create_task(
                    sw.track(
                        user_id=request.user.id,
                        entity_id=entity_id,
                        action=request.method.lower(),
                        metadata={
                            'path': request.path,
                            'ip': self._get_client_ip(request)
                        }
                    )
                )
        
        response = self.get_response(request)
        return response
    
    def _extract_entity_id(self, request):
        # Example: /stocks/AAPL/ → "AAPL"
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'stocks':
            return path_parts[1]
        return None
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

**5. Add middleware to settings:**

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'middleware.shadowwatch_middleware.ShadowWatchMiddleware',
]
```

**6. Manual tracking in views:**

```python
# views.py
from shadowwatch_instance import sw
from django.http import JsonResponse
import asyncio

async def trade_view(request):
    if request.method == 'POST':
        # Parse trade data
        symbol = request.POST.get('symbol')
        quantity = int(request.POST.get('quantity'))
        price = float(request.POST.get('price'))
        
        # Track trade
        await sw.track(
            user_id=request.user.id,
            entity_id=symbol,
            action='trade',
            metadata={
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            }
        )
        
        # Execute trade
        result = execute_trade(request.user, symbol, quantity, price)
        return JsonResponse(result)
```

---

## Flask Integration

### Basic Setup (10 Minutes)

**1. Install Shadow Watch:**

```bash
pip install shadowwatch
```

**2. Initialize in your app:**

```python
# app.py
from flask import Flask, request, g
from shadowwatch import ShadowWatch
import os
import asyncio

app = Flask(__name__)

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE_KEY"),
    redis_url=os.getenv("REDIS_URL")  # Production only
)
```

**3. Create before_request hook:**

```python
@app.before_request
def before_request():
    # Store user ID in g object
    if 'user_id' in session:
        g.user_id = session['user_id']
    else:
        g.user_id = None
```

**4. Create after_request hook for tracking:**

```python
@app.after_request
def after_request(response):
    # Track activity if user is authenticated
    if g.user_id and request.endpoint:
        # Extract entity ID from URL
        entity_id = request.view_args.get('symbol') if request.view_args else None
        
        if entity_id:
            # Track asynchronously
            asyncio.run(
                sw.track(
                    user_id=g.user_id,
                    entity_id=entity_id,
                    action=request.method.lower(),
                    metadata={
                        'endpoint': request.endpoint,
                        'ip': request.remote_addr
                    }
                )
            )
    
    return response
```

**5. Manual tracking in routes:**

```python
@app.route('/stocks/<symbol>')
def get_stock(symbol):
    # Automatic tracking via after_request hook
    
    return {
        "symbol": symbol,
        "price": 185.20
    }

@app.route('/trades', methods=['POST'])
def create_trade():
    data = request.get_json()
    
    # Manual tracking with metadata
    asyncio.run(
        sw.track(
            user_id=g.user_id,
            entity_id=data['symbol'],
            action='trade',
            metadata={
                'side': data['side'],
                'quantity': data['quantity'],
                'price': data['price']
            }
        )
    )
    
    # Execute trade
    result = execute_trade(data)
    return result
```

---

## General Python Application

### For Non-Web Applications

**Use Shadow Watch directly without middleware:**

```python
# main.py
import asyncio
from shadowwatch import ShadowWatch
import os

# Initialize
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE_KEY")
)

async def main():
    user_id = 123
    
    # User views portfolio
    await sw.track(user_id=user_id, entity_id="PORTFOLIO", action="view")
    
    # User searches for tech stocks
    await sw.track(
        user_id=user_id,
        entity_id="TECH_STOCKS",
        action="search",
        metadata={"query": "tech stocks"}
    )
    
    # User executes trade
    await sw.track(
        user_id=user_id,
        entity_id="AAPL",
        action="trade",
        metadata={"quantity": 10, "price": 185.20}
    )
    
    # Get user profile
    profile = await sw.get_profile(user_id=user_id)
    print(f"User has {profile['total_items']} interests")
    print(f"Top interest: {profile['library'][0]['entity_id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Production Checklist

### Before Deploying to Production

- [ ] Use environment variables for credentials
- [ ] Enable Redis for multi-instance deployments
- [ ] Set up database indexes (see API Reference)
- [ ] Configure logging level (`INFO` or `WARNING`)
- [ ] Test license verification works
- [ ] Test behavioral fingerprinting works
- [ ] Monitor database query performance
- [ ] Set up error alerts (Sentry, etc.)
- [ ] Document internal deployment process
- [ ] Train team on Shadow Watch concepts

---

### Environment Variables

```bash
# Required
SHADOWWATCH_LICENSE_KEY=SW-PROD-XXXX-XXXX-XXXX-XXXX
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# Recommended for production
REDIS_URL=redis://localhost:6379

# Optional
SHADOWWATCH_LOG_LEVEL=INFO
```

---

### Database Migrations

**For SQLAlchemy:**

```python
from shadowwatch.models import Base
from sqlalchemy import create_engine

engine = create_engine(database_url.replace('+asyncpg', ''))  # Sync engine
Base.metadata.create_all(engine)
```

**For Alembic:**

```bash
# Generate migration
alembic revision --autogenerate -m "Add Shadow Watch tables"

# Apply migration
alembic upgrade head
```

---

### Performance Tuning

**1. Database Indexes:**

```sql
CREATE INDEX idx_activity_user_id ON shadow_watch_activity_events(user_id);
CREATE INDEX idx_activity_created_at ON shadow_watch_activity_events(created_at);
CREATE INDEX idx_interests_user_id ON shadow_watch_interests(user_id);
CREATE INDEX idx_interests_score ON shadow_watch_interests(score DESC);
```

**2. Redis Configuration:**

```bash
# In production, increase max memory
maxmemory 512mb
maxmemory-policy allkeys-lru
```

**3. Connection Pooling:**

```python
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10
)
```

---

## Troubleshooting

### Common Issues

**1. "AsyncIO event loop is already running"**

**Solution:** Use `asyncio.create_task()` instead of `asyncio.run()`

```python
# ❌ DON'T
asyncio.run(sw.track(...))

# ✅ DO
asyncio.create_task(sw.track(...))
```

---

**2. "License verification failed"**

**Solution:** Check network connectivity to license server

```bash
curl https://shadow-watch-three.vercel.app/verify
```

---

**3. "Redis connection refused"**

**Solution:** Either remove `redis_url` (use memory) or start Redis:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

---

## Support

- **Documentation:** https://github.com/Tanishq1030/Shadow_Watch
- **Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com

---

**Last Updated:** January 11, 2026  
**Version:** 0.1.0
