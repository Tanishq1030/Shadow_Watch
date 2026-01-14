import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { TerminalDemo } from '@/components/docs/TerminalDemo';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Installation = () => {
    const INIT_CODE = `from shadowwatch import ShadowWatch
import asyncio

async def main():
    # Initialize Shadow Watch
    sw = ShadowWatch(
        database_url="postgresql+asyncpg://localhost:5432/mydb",
        license_key="SW-TRIAL-YOUR-KEY-HERE"
    )
    
    # Create tables automatically
    await sw.init_database()
    print("✅ Shadow Watch initialized!")

if __name__ == "__main__":
    asyncio.run(main())`;

    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Installation & Quick Start</h1>
                    <p className="text-xl text-zinc-400">
                        From zero to tracking in one coffee break (15 minutes)
                    </p>
                </div>

                <Terminal>
                    <TerminalHeader>
                        <span className="text-green-500">$</span> cat timer.txt
                    </TerminalHeader>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            You have <span className="text-yellow-500">15 minutes</span> before your next meeting.
                            Your boss wants to know if behavioral tracking is "hard to implement."<br />
                            <span className="text-zinc-500"># Let's find out together...</span>
                        </p>
                    </TerminalBody>
                </Terminal>

                <section id="prerequisites" className="mb-12">
                    <h2 className="mb-6">Prerequisites</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch check --requirements
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="grid md:grid-cols-2 gap-8 font-mono text-sm">
                                <div>
                                    <div className="text-green-500 font-bold mb-2">Required:</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>• Python 3.8 or higher</div>
                                        <div>• PostgreSQL, MySQL, or SQLite</div>
                                        <div>• pip or poetry</div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-yellow-500 font-bold mb-2">Recommended:</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>• Redis (production caching)</div>
                                        <div>• FastAPI or Django project</div>
                                        <div>• Basic async/await knowledge</div>
                                    </div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="installation-methods" className="mb-12">
                    <h2 className="mb-6">Installation Methods</h2>

                    <div className="space-y-6">
                        <div>
                            <h3 className="text-xl font-bold mb-3">1. Using pip (Recommended)</h3>
                            <CodeBlock code="pip install shadowwatch" language="bash" />
                        </div>

                        <div>
                            <h3 className="text-xl font-bold mb-3">2. Using Poetry</h3>
                            <CodeBlock code="poetry add shadowwatch" language="bash" />
                        </div>

                        <div>
                            <h3 className="text-xl font-bold mb-3">3. Using requirements.txt</h3>
                            <CodeBlock
                                code={`# requirements.txt
shadowwatch>=2.1.0
postgresql-asyncpg>=0.27.0  # For PostgreSQL
redis>=4.5.0               # For caching (production)`}
                                filename="requirements.txt"
                            />
                            <CodeBlock code="pip install -r requirements.txt" language="bash" />
                        </div>
                    </div>
                </section>

                <section id="configuration" className="mb-12">
                    <h2 className="mb-6">Configuration</h2>

                    <p className="mb-4">Set up your environment variables:</p>

                    <CodeBlock
                        code={`# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb
SHADOWWATCH_LICENSE=SW-TRIAL-YOUR-KEY-HERE
REDIS_URL=redis://localhost:6379  # Optional, for production`}
                        filename=".env"
                    />

                    <Terminal>
                        <TerminalBody mode="text">
                            <p className="text-sm text-zinc-400">
                                <span className="text-yellow-500">!!</span> Get a free trial license: Visit{' '}
                                <Link to="/get-license" className="text-green-500 hover:underline">/get-license</Link>
                                {' '}to generate a 30-day trial key instantly.
                            </p>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="database-init" className="mb-12">
                    <h2 className="mb-6">Database Initialization</h2>

                    <p className="mb-4">Create a setup script to initialize Shadow Watch tables:</p>

                    <TerminalDemo
                        title="init_shadowwatch.py"
                        mode="code"
                        code={INIT_CODE}
                        autoplay
                    />

                    <p className="mt-4 mb-2">Run it once:</p>
                    <CodeBlock code="python init_db.py" language="bash" />
                </section>

                <section id="first-integration" className="mb-12">
                    <h2 className="mb-6">First Integration (FastAPI)</h2>

                    <p className="mb-4">Add Shadow Watch to your FastAPI app in 3 steps:</p>

                    <CodeBlock
                        code={`from fastapi import FastAPI
from shadowwatch import ShadowWatch
import os

app = FastAPI()

# Step 1: Initialize Shadow Watch
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE")
)

# Step 2: Track an activity
@app.get("/items/{item_id}")
async def get_item(item_id: str, user_id: int):
    # Track the view
    await sw.track(
        user_id=user_id,
        entity_id=item_id,
        action="view"
    )
    
    return {"item_id": item_id, "title": "Example Item"}

# Step 3: Check user profile
@app.get("/users/{user_id}/profile")
async def get_profile(user_id: int):
    profile = await sw.get_profile(user_id)
    return profile`}
                        language="python"
                        filename="main.py"
                    />

                    <p className="text-green-500 font-bold mt-6">That's it! 🎉 Shadow Watch is now tracking user behavior.</p>
                </section>

                <section id="verification" className="mb-12">
                    <h2 className="mb-6">Verification</h2>

                    <p className="mb-4">Test your integration:</p>

                    <div className="space-y-4">
                        <div>
                            <h3 className="text-lg font-bold mb-2">1. Start your server</h3>
                            <CodeBlock code="uvicorn main:app --reload" language="bash" />
                        </div>

                        <div>
                            <h3 className="text-lg font-bold mb-2">2. Track an event</h3>
                            <CodeBlock code='curl "http://localhost:8000/items/product-123?user_id=1"' language="bash" />
                        </div>

                        <div>
                            <h3 className="text-lg font-bold mb-2">3. Check the profile</h3>
                            <CodeBlock code='curl "http://localhost:8000/users/1/profile"' language="bash" />
                        </div>
                    </div>

                    <p className="mt-6 mb-2">Expected response:</p>

                    <CodeBlock
                        code={`{
  "total_items": 1,
  "fingerprint": "a3f2c1b...",
  "library": [
    {
      "entity_id": "product-123",
      "view_count": 1,
      "last_viewed": "2024-01-13T01:21:00Z"
    }
  ],
  "pinned_count": 0
}`}
                        language="json"
                    />
                </section>

                <div className="border-l-4 border-green-500 bg-black p-6 mb-12 rounded">
                    <h3 className="text-lg font-bold flex items-center gap-2 mb-2">
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                        You Did It!
                    </h3>
                    <p className="text-zinc-300">
                        In 15 minutes, you installed Shadow  Watch, initialized the database, and integrated it into your app.
                        Now you can tell your boss: <span className="text-green-500">"It's literally 3 steps."</span>
                    </p>
                </div>

                <section className="mb-12">
                    <h2 className="mb-6">Next Steps</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <Link to="/docs/fastapi-integration" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Production FastAPI Guide
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    Complete production example with middleware and trust scores
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/postgresql" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    PostgreSQL Setup
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    Scale to millions of users with PostgreSQL + Redis
                                </p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
