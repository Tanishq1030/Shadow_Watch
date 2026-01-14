import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const StandaloneUsage = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Standalone Usage</h1>
                    <p className="text-xl text-zinc-400">
                        Running Shadow Watch as a microservice
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            Don't want to embed Shadow Watch in your app? Run it as a standalone microservice.
                            Perfect for <span className="text-green-500">polyglot architectures</span> (Node.js frontend, Python backend, etc.)
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Architecture</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch architecture
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-sm space-y-2">
                                <div className="text-zinc-400">Your App (Any Language)</div>
                                <div className="text-zinc-600">    ↓ HTTP POST</div>
                                <div className="text-green-500">Shadow Watch Service (FastAPI)</div>
                                <div className="text-zinc-600">    ↓</div>
                                <div className="text-zinc-400">PostgreSQL + Redis</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <h3 className="text-xl font-bold mt-8 mb-4">Create the Service</h3>

                    <CodeBlock
                        code={`from fastapi import FastAPI, HTTPException
from shadowwatch import ShadowWatch
from pydantic import BaseModel
import os

app = FastAPI(title="Shadow Watch Service")

sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE"),
    redis_url=os.getenv("REDIS_URL")
)

@app.on_event("startup")
async def startup():
    await sw.init_database()

class TrackRequest(BaseModel):
    user_id: int
    entity_id: str
    action: str
    metadata: dict = {}

@app.post("/track")
async def track(req: TrackRequest):
    await sw.track(
        user_id=req.user_id,
        entity_id=req.entity_id,
        action=req.action,
        metadata=req.metadata
    )
    return {"status": "tracked"}

@app.get("/profile/{user_id}")
async def get_profile(user_id: int):
    profile = await sw.get_profile(user_id)
    return profile

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)`}
                        language="python"
                        filename="service.py"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Call from Any Language</h3>

                    <CodeBlock
                        code={`// JavaScript/Node.js
const response = await fetch('http://shadow-watch:8000/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 42,
        entity_id: 'product-123',
        action: 'view',
        metadata: { source: 'mobile' }
    })
});

// Get profile
const profile = await fetch('http://shadow-watch:8000/profile/42');
const data = await profile.json();
console.log(data.fingerprint);`}
                        language="javascript"
                    />

                    <CodeBlock
                        code={`# Ruby
require 'net/http'
require 'json'

uri = URI('http://shadow-watch:8000/track')
req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
req.body = {
  user_id: 42,
  entity_id: 'product-123',
  action: 'view'
}.to_json

Net::HTTP.start(uri.hostname, uri.port) { |http| http.request(req) }`}
                        language="ruby"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Docker Deployment</h2>

                    <CodeBlock
                        code={`# docker-compose.yml
version: '3.8'

services:
  shadow-watch:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@postgres:5432/shadowwatch
      SHADOWWATCH_LICENSE: SW-TRIAL-YOUR-KEY
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: shadowwatch
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:`}
                        filename="docker-compose.yml"
                    />

                    <p className="mt-4 mb-2">Start the service:</p>
                    <CodeBlock code="docker-compose up -d" language="bash" />
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
                                <p className="text-sm text-zinc-400">Scale to production</p>
                            </div>
                        </Link>

                        <Link to="/docs/redis" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Redis Caching
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">Multi-instance deployments</p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
