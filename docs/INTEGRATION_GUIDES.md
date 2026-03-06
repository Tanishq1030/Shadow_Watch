# Shadow Watch — Integration Guides

Step-by-step guides for integrating Shadow Watch into popular Python frameworks.

---

## Table of Contents

- [FastAPI Integration](#fastapi-integration)
- [Django Integration](#django-integration)
- [Flask Integration](#flask-integration)
- [General Python Application](#general-python-application)
- [Production Checklist](#production-checklist)

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
from fastapi import FastAPI, Request
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware
import os

app = FastAPI()

sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")  # Optional — for multi-instance deployments
)

@app.on_event("startup")
async def startup():
    await sw.init_database()

# Auto-track all authenticated requests
app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    extract_user_id=lambda request: getattr(request.state, "user_id", None),
    extract_entity_id=lambda request: request.path_params.get("symbol"),
    extract_action=lambda request: request.method.lower()
)
```

**3. Add authentication middleware:**

```python
import jwt

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.state.user_id = payload.get("user_id")
        except jwt.InvalidTokenError:
            pass
    return await call_next(request)
```

**4. Your routes now auto-track:**

```python
@app.get("/stocks/{symbol}")
async def get_stock(symbol: str):
    # Shadow Watch silently tracks: user_id, symbol, "get"
    return {"symbol": symbol, "price": 185.20}
```

---

### Custom Tracking with Metadata

```python
from fastapi import Depends

def get_sw():
    return sw

@app.post("/trades")
async def create_trade(
    trade: TradeData,
    request: Request,
    sw: ShadowWatch = Depends(get_sw)
):
    await sw.track(
        user_id=request.state.user_id,
        entity_id=trade.symbol,
        action="trade",
        metadata={
            "side": trade.side,
            "quantity": trade.quantity,
            "price": trade.price,
            "total": trade.quantity * trade.price
        }
    )
    return execute_trade(trade)
```

---

### Login Verification Integration

```python
@app.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    user = await authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    trust = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.cookies.get("device_fp"),
        }
    )

    if trust["action"] == "allow":
        return {"token": generate_jwt(user.id)}

    elif trust["action"] == "require_mfa":
        send_mfa_code(user.id)
        return {"require_mfa": True, "message": "Check your phone"}

    else:  # block
        send_security_alert(user.id, request.client.host)
        raise HTTPException(403, "Suspicious login attempt detected")
```

---

## Django Integration

### Basic Setup (10 Minutes)

**1. Install:**

```bash
pip install shadowwatch
```

**2. Add to settings:**

```python
# settings.py
import os

SHADOWWATCH_CONFIG = {
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'REDIS_URL': os.getenv('REDIS_URL'),  # Optional
}
```

**3. Create a shared instance:**

```python
# shadowwatch_instance.py
from shadowwatch import ShadowWatch
from django.conf import settings
import asyncio

sw = ShadowWatch(
    database_url=settings.SHADOWWATCH_CONFIG['DATABASE_URL'],
    redis_url=settings.SHADOWWATCH_CONFIG.get('REDIS_URL')
)

# Initialize tables (run once)
asyncio.run(sw.init_database())
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
        if request.user.is_authenticated:
            entity_id = self._extract_entity_id(request)
            if entity_id:
                asyncio.create_task(
                    sw.track(
                        user_id=request.user.id,
                        entity_id=entity_id,
                        action=request.method.lower(),
                        metadata={"path": request.path}
                    )
                )
        return self.get_response(request)

    def _extract_entity_id(self, request):
        parts = request.path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] in ('stocks', 'products', 'items'):
            return parts[1]
        return None
```

**5. Register middleware:**

```python
# settings.py
MIDDLEWARE = [
    # ... existing middleware
    'middleware.shadowwatch_middleware.ShadowWatchMiddleware',
]
```

**6. Manual tracking in views:**

```python
# views.py
from shadowwatch_instance import sw
from django.http import JsonResponse

async def trade_view(request):
    symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    price = float(request.POST.get('price'))

    await sw.track(
        user_id=request.user.id,
        entity_id=symbol,
        action='trade',
        metadata={'quantity': quantity, 'price': price}
    )

    result = execute_trade(request.user, symbol, quantity, price)
    return JsonResponse(result)
```

---

## Flask Integration

### Basic Setup (10 Minutes)

**1. Install:**

```bash
pip install shadowwatch
```

**2. Initialize:**

```python
# app.py
from flask import Flask, request, g, session
from shadowwatch import ShadowWatch
import os, asyncio

app = Flask(__name__)

sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")
)

asyncio.run(sw.init_database())
```

**3. Track via hooks:**

```python
@app.before_request
def set_user():
    g.user_id = session.get('user_id')

@app.after_request
def track_activity(response):
    if g.get('user_id') and request.view_args:
        entity_id = request.view_args.get('symbol')
        if entity_id:
            try:
                asyncio.run(
                    sw.track(
                        user_id=g.user_id,
                        entity_id=entity_id,
                        action=request.method.lower()
                    )
                )
            except Exception:
                pass  # Never block the response
    return response
```

**4. Routes:**

```python
@app.route('/stocks/<symbol>')
def get_stock(symbol):
    # Auto-tracked via after_request
    return {"symbol": symbol, "price": 185.20}

@app.route('/trades', methods=['POST'])
def create_trade():
    data = request.get_json()
    asyncio.run(
        sw.track(
            user_id=g.user_id,
            entity_id=data['symbol'],
            action='trade',
            metadata={'side': data['side'], 'quantity': data['quantity']}
        )
    )
    return execute_trade(data)
```

---

## General Python Application

For scripts, CLIs, and non-web applications:

```python
import asyncio, os
from shadowwatch import ShadowWatch

sw = ShadowWatch(database_url=os.getenv("DATABASE_URL"))

async def main():
    await sw.init_database()

    user_id = 123

    await sw.track(user_id=user_id, entity_id="PORTFOLIO", action="view")
    await sw.track(user_id=user_id, entity_id="AAPL", action="search")
    await sw.track(
        user_id=user_id,
        entity_id="AAPL",
        action="trade",
        metadata={"quantity": 10, "price": 185.20}
    )

    profile = await sw.get_profile(user_id=user_id)
    print(f"User has {profile['total_items']} tracked interests")

    continuity = await sw.calculate_continuity(str(user_id))
    print(f"Continuity score: {continuity['score']} ({continuity['state']})")

asyncio.run(main())
```

---

## Production Checklist

### Before Deploying

- [ ] `DATABASE_URL` set via environment variable (never hardcoded)
- [ ] `await sw.init_database()` called on startup
- [ ] `REDIS_URL` configured for multi-instance / multi-worker setups
- [ ] Database indexes created (see [API Reference](./API_REFERENCE.md#recommended-database-indexes))
- [ ] Logging level set (`INFO` or `WARNING`)
- [ ] Tracking wrapped in `try/except` — Shadow Watch must never crash your app
- [ ] `verify_login()` integrated at login endpoints for ATO protection
- [ ] GDPR: `export_user_data()` and `delete_user()` endpoints wired up

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Recommended for production (multi-instance)
REDIS_URL=redis://localhost:6379

# Optional
SHADOWWATCH_LOG_LEVEL=INFO
```

### Database Migrations (Alembic)

```bash
alembic revision --autogenerate -m "Add Shadow Watch tables"
alembic upgrade head
```

### Connection Pooling (High Traffic)

```python
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10
)
```

### Redis Configuration (Production)

```bash
maxmemory 512mb
maxmemory-policy allkeys-lru
```

---

## Troubleshooting

**`RuntimeError: This event loop is already running`**

Use `asyncio.create_task()` instead of `asyncio.run()` inside async contexts:

```python
# ❌ Inside async context
asyncio.run(sw.track(...))

# ✅ Inside async context
asyncio.create_task(sw.track(...))
```

**`Redis connection refused`**

Remove `redis_url` to use in-memory cache (fine for single instance), or start Redis:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**`UndefinedTableError`**

You haven't called `await sw.init_database()` yet.

---

## Support

- **GitHub:** https://github.com/Tanishq1030/Shadow_Watch
- **Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com

---

**Version:** 2.0.0 — Free and open source (MIT)
