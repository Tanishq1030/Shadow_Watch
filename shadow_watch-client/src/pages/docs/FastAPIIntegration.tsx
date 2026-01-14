import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { TerminalDemo } from '@/components/docs/TerminalDemo';
import { CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FastAPIIntegration = () => {
    // Code constants for typing animation
    const SETUP_CODE = `from fastapi import FastAPI
from shadowwatch import ShadowWatch
import os

app = FastAPI(title="QuantForge Terminal")

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE"),
    redis_url=os.getenv("REDIS_URL")  # Production caching
)

# Create tables on startup
@app.on_event("startup")
async def startup():
    await sw.init_database()
    print("✅ Shadow Watch initialized")`;

    const MIDDLEWARE_CODE = `from shadowwatch.integrations.fastapi import add_shadow_watch

# Add Shadow Watch middleware
add_shadow_watch(
    app,
    shadow_watch=sw,
    user_id_getter=lambda req: getattr(req.state, 'user_id', None)
)

# Now ALL requests are automatically tracked!
@app.get("/stocks/{symbol}")
async def get_stock(symbol: str, request: Request):
    # Set user from auth (your existing auth middleware)
    request.state.user_id = get_current_user(request).id
    
    # Shadow Watch tracks this automatically
    return {"symbol": symbol, "price": 42.50}`;

    const TRACKING_CODE = `@app.post("/watchlist/add")
async def add_to_watchlist(symbol: str, user_id: int):
    # Add to database
    await db.watchlist.add(user_id, symbol)
    
    # Explicitly track with metadata
    await sw.track(
        user_id=user_id,
        entity_id=symbol,
        action="watchlist_add",
        metadata={
            "price": await get_current_price(symbol),
            "market": "NYSE"
        }
    )
    
    return {"status": "added"}

@app.post("/trades/execute")
async def execute_trade(trade: TradeOrder, user_id: int):
    # Execute trade
    result = await execute_order(trade)
    
    # Track with detailed metadata
    await sw.track(
        user_id=user_id,
        entity_id=trade.symbol,
        action="trade_execute",
        metadata={
            "side": trade.side,  # buy/sell
            "quantity": trade.quantity,
            "price": trade.price,
            "total_value": trade.quantity * trade.price
        }
    )
    
    return result`;

    const LOGIN_CODE = `from fastapi import HTTPException

@app.post("/auth/login")
async def login(email: str, password: str, request: Request):
    # 1. Validate credentials (your existing logic)
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 2. Calculate trust score
    trust_result = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "country": get_country_from_ip(request.client.host),
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.headers.get("x-device-id"),
            "timestamp": datetime.now()
        }
    )
    
    # 3. Act based on trust score
    if trust_result["action"] == "block":
        # Log the attempt
        await log_security_event(user.id, "login_blocked", trust_result)
        
        # Notify user via email
        await send_security_alert(user.email, trust_result)
        
        raise HTTPException(
            status_code=403,
            detail="Suspicious login attempt detected. Check your email."
        )
    
    elif trust_result["action"] == "require_mfa":
        # Force 2FA even if they have it disabled
        return {"status": "mfa_required", "token": generate_mfa_token(user)}
    
    # 4. Allow login
    return {"token": create_jwt_token(user), "trust_score": trust_result["trust_score"]}`;

    const COMPLETE_CODE = `from fastapi import FastAPI, Request, HTTPException
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import add_shadow_watch
from datetime import datetime
import os

app = FastAPI(title="QuantForge Terminal")

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE"),
    redis_url=os.getenv("REDIS_URL")
)

@app.on_event("startup")
async def startup():
    await sw.init_database()

# Add middleware for automatic tracking
add_shadow_watch(
    app,
    shadow_watch=sw,
    user_id_getter=lambda req: getattr(req.state, 'user_id', None)
)

# Stock view endpoint (auto-tracked)
@app.get("/stocks/{symbol}")
async def get_stock(symbol: str, request: Request):
    request.state.user_id = 1  # From your auth
    return {"symbol": symbol, "price": 42.50}

# Login with trust score
@app.post("/auth/login")
async def login(email: str, password: str, request: Request):
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    trust_result = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.now()
        }
    )
    
    if trust_result["action"] == "block":
        raise HTTPException(403, "Suspicious login blocked")
    
    return {"token": "...", "trust_score": trust_result["trust_score"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)`;

    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">FastAPI Integration</h1>
                    <p className="text-xl text-zinc-400">
                        Securing QuantForge: A real production journey
                    </p>
                </div>

                <section id="quantforge-story" className="mb-12">
                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> cat quantforge_story.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <p className="text-zinc-300 mb-3">
                                QuantForge Terminal had <span className="text-green-500">10,000 users</span> trading millions of dollars.
                                One compromised account could be catastrophic.Traditional auth wasn't enough.
                            </p>
                            <p className="text-zinc-300">
                                Here's how Shadow Watch was integrated in <span className="text-green-500">2 hours</span>...
                            </p>
                        </TerminalBody>
                    </Terminal>

                    <div className="grid grid-cols-3 gap-4 mt-6">
                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-500 mb-1">10K</div>
                                    <div className="text-xs text-zinc-500">Active users</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-500 mb-1">2hr</div>
                                    <div className="text-xs text-zinc-500">Integration time</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-red-500 mb-1">3</div>
                                    <div className="text-xs text-zinc-500">Attacks blocked (Week 1)</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                <section id="project-setup" className="mb-12">
                    <h2 className="mb-6">Project Setup</h2>

                    <p className="mb-4">The QuantForge team started with a basic FastAPI project:</p>

                    <TerminalDemo
                        title="main.py"
                        mode="code"
                        code={SETUP_CODE}
                        autoplay
                    />
                </section>

                <section id="middleware" className="mb-12">
                    <h2 className="mb-6">Middleware Integration</h2>

                    <p className="mb-4">
                        Instead of manually tracking every endpoint, they used middleware for automatic tracking:
                    </p>

                    <TerminalDemo
                        title="middleware.py"
                        mode="code"
                        code={MIDDLEWARE_CODE}
                        autoplay
                    />

                    <Terminal>
                        <TerminalBody mode="text">
                            <p className="text-sm text-zinc-400 flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                <span>
                                    <strong className="text-green-500">Result:</strong> All stock views, watchlist changes, and trade actions
                                    are now automatically tracked without modifying existing endpoints.
                                </span>
                            </p>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="tracking" className="mb-12">
                    <h2 className="mb-6">Explicit Activity Tracking</h2>

                    <p className="mb-4">
                        For critical actions, they added explicit tracking with metadata:
                    </p>

                    <TerminalDemo
                        title="trading_endpoints.py"
                        mode="code"
                        code={TRACKING_CODE}
                        autoplay
                    />
                </section>

                <section id="trust-scores" className="mb-12">
                    <h2 className="mb-6">Trust Score on Login</h2>

                    <p className="mb-4">
                        The critical integration: blocking suspicious logins before they access trading accounts:
                    </p>

                    <TerminalDemo
                        title="auth.py"
                        mode="code"
                        code={LOGIN_CODE}
                        autoplay
                    />

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch results --week 1
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <p className="font-bold text-white mb-3">Real Results:</p>
                            <p className="text-sm text-zinc-300 mb-3">
                                In the first week, Shadow Watch blocked 3 account takeover attempts:
                            </p>
                            <div className="space-y-1 text-sm font-mono text-zinc-400">
                                <div>• Nigerian IP → US account <span className="text-red-500">(trust: 0.12)</span></div>
                                <div>• 3 AM login from new device <span className="text-red-500">(trust: 0.31)</span></div>
                                <div>• Rapid stock views <span className="text-red-500">(entropy: 0.95)</span></div>
                            </div>
                            <p className="text-green-500 font-bold mt-4 text-sm">
                                ✓ All blocked before accessing trading functionality.
                            </p>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="deployment" className="mb-12">
                    <h2 className="mb-6">Production Deployment</h2>

                    <p className="mb-4">QuantForge deployed with Docker and Vercel:</p>

                    <CodeBlock
                        code={`# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables set in Vercel/cloud
# DATABASE_URL, SHADOWWATCH_LICENSE, REDIS_URL

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`}
                        filename="Dockerfile"
                    />

                    <h3 className="text-lg font-bold mt-6 mb-3">Environment Variables (Production)</h3>
                    <CodeBlock
                        code={`DATABASE_URL=postgresql+asyncpg://user:pass@aws-rds.amazonaws.com:5432/quantforge
SHADOWWATCH_LICENSE=SW-PROD-QUANTFORGE-2024-XYZ123
REDIS_URL=redis://redis-cloud.redislabs.com:12345`}
                        filename=".env.production"
                    />

                    <div className="grid md:grid-cols-2 gap-6 mt-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-red-500">✗</span> Before Shadow Watch
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-1 text-sm text-zinc-400">
                                    <div>• 2-3 account takeovers per month</div>
                                    <div>• Manual investigation required</div>
                                    <div>• Users complained about security</div>
                                    <div className="text-red-500">• $50K+ in fraudulent trades (avg)</div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">✓</span> After Shadow Watch
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-1 text-sm text-zinc-400">
                                    <div className="text-green-500">• 0 successful takeovers in 3 months</div>
                                    <div>• Automatic blocking</div>
                                    <div>• User trust increased</div>
                                    <div className="text-green-500">• $0 in fraud losses</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Complete Working Example</h2>

                    <p className="mb-4">Here's the full integration code:</p>

                    <TerminalDemo
                        title="complete_example.py"
                        mode="code"
                        code={COMPLETE_CODE}
                        autoplay
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Next Steps</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <Link to="/docs/postgresql" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    PostgreSQL Setup
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    Scale to millions with proper database configuration
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/redis" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Redis Caching
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    Multi-instance deployment with shared state
                                </p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
