import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { TerminalDemo } from '@/components/docs/TerminalDemo';
import { CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const GettingStarted = () => {
    // Code examples
    const INIT_CODE = `from shadowwatch import ShadowWatch

# Initialize with your database
sw = ShadowWatch(
    database_url="sqlite:///data.db",
    license_key="SW-TRIAL-YOUR-KEY-HERE"
)

# Create tables automatically
await sw.init_database()
print("✅ Shadow Watch initialized!")`;

    const DB_SETUP_CODE = `from shadowwatch import ShadowWatch
import asyncio

async def main():
    # Initialize Shadow Watch
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./shadowwatch.db",
        license_key="SW-TRIAL-YOUR-KEY-HERE"
    )
    
    # Create tables automatically
    await sw.init_database()
    print("✅ Shadow Watch initialized!")

if __name__ == "__main__":
    asyncio.run(main())`;

    const TRACK_CODE = `# Track user activity
await sw.track_activity(
    user_id="user_123",
    action="login",
    metadata={
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
)

print("✅ Activity tracked!")`;

    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="mb-16">
                    <h1 className="mb-6">
                        Your First Detection in 5 Minutes
                    </h1>
                    <p className="text-xl text-zinc-400 leading-relaxed">
                        Watch Sarah, a backend developer, add behavioral intelligence to her API
                        before her morning standup. No ML degree required. No complex setup.
                    </p>
                </div>

                {/* The Story */}
                <section id="the-story" className="mb-16">
                    <Terminal>
                        <TerminalHeader>
                            cat story.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-4 text-zinc-300">
                                <p>
                                    <span className="text-yellow-500">[9:55 AM]</span> Sarah's Challenge
                                </p>
                                <p>
                                    Sarah has 5 minutes before standup. Her CEO just asked:
                                    <span className="text-yellow-500"> "Can we detect if someone's account gets hacked?"</span>
                                </p>
                                <p>
                                    She needs something that works <span className="text-green-500">NOW</span>.
                                    Not in a sprint. Not after reading 50 pages of ML documentation.
                                </p>
                                <p className="text-zinc-500">
                                    Let's watch what happens...
                                </p>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                {/* What You'll Build */}
                <section id="what-youll-build" className="mb-16">
                    <h2 className="mb-8">What You'll Build</h2>

                    <Terminal>
                        <TerminalHeader>
                            cat checklist.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono">
                                <div><span className="text-green-500">✓</span> Shadow Watch installed and running</div>
                                <div><span className="text-green-500">✓</span> Database tables created automatically</div>
                                <div><span className="text-green-500">✓</span> Your first user activity tracked</div>
                                <div><span className="text-green-500">✓</span> Real behavioral profile generated</div>
                                <div><span className="text-green-500">✓</span> Understanding of how it all works</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                {/* Installation */}
                <section id="installation" className="mb-16">
                    <h2 className="mb-8">Step 1: Installation</h2>

                    <p className="mb-6">
                        Sarah opens her terminal. One command. That's it.
                    </p>

                    <CodeBlock
                        code="pip install shadowwatch"
                        language="bash"
                    />

                    <p className="mt-6 mb-6">
                        30 seconds later, Shadow Watch is installed. Next: initialization.
                    </p>

                    {/* FIRST TYPING ANIMATION EXAMPLE */}
                    <TerminalDemo
                        title="init_shadow_watch.py"
                        mode="code"
                        language="python"
                        code={INIT_CODE}
                        autoplay
                    />

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> What just happened?
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-3">
                                <p className="text-zinc-300">
                                    <span className="text-green-500">1.</span> Package Download: Pip fetched Shadow Watch from PyPI (~2.3MB)
                                </p>
                                <p className="text-zinc-300">
                                    <span className="text-green-500">2.</span> Dependencies: SQLAlchemy, Pydantic, cryptography
                                </p>
                                <p className="text-zinc-300">
                                    <span className="text-green-500">3.</span> License Validator: Checks your key (offline after first use)
                                </p>
                                <p className="text-zinc-300">
                                    <span className="text-green-500">4.</span> Ready: <code>from shadowwatch import ShadowWatch</code> now works
                                </p>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    {/* Database Setup */}
                    <div id="database-setup" className="mt-12">
                        <h3 className="mb-6">Database Setup</h3>

                        <p className="mb-6">
                            Shadow Watch needs a database to store user profiles.
                        </p>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> ls databases/
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-2 font-mono">
                                    <div className="text-green-500">postgresql/  <span className="text-zinc-500"># Recommended for production</span></div>
                                    <div className="text-yellow-500">mysql/       <span className="text-zinc-500"># Enterprise-friendly</span></div>
                                    <div className="text-zinc-400">sqlite/       <span className="text-zinc-500"># Perfect for testing</span></div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <p className="my-6">
                            Sarah chooses SQLite for local testing:
                        </p>

                        <TerminalDemo
                            title="init_shadow_watch.py"
                            mode="code"
                            code={DB_SETUP_CODE}
                            autoplay
                        />
                    </div>

                    {/* Initialization Deep Dive */}
                    <div id="initialization" className="mt-12">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch explain init_database()
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-4">
                                    <p className="text-zinc-300">
                                        This single line creates <span className="text-green-500">4 tables</span> in your database:
                                    </p>

                                    <div className="space-y-2 font-mono text-sm">
                                        <div className="text-green-500">
                                            user_activities <span className="text-zinc-500">→ Raw events with timestamps</span>
                                        </div>
                                        <div className="text-green-500">
                                            user_profiles <span className="text-zinc-500">→ Behavioral fingerprints, entropy</span>
                                        </div>
                                        <div className="text-green-500">
                                            interest_library <span className="text-zinc-500">→ What users love (frequency, recency)</span>
                                        </div>
                                        <div className="text-green-500">
                                            trust_events <span className="text-zinc-500">→ Login attempts, trust scores</span>
                                        </div>
                                    </div>

                                    <p className="text-zinc-500 text-sm mt-4">
                                        Execution time: ~150ms (first run), &lt;5ms (subsequent)
                                    </p>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* First Track Event */}
                <section id="first-track" className="mb-16">
                    <h2 className="mb-8">Step 2: Track Your First Activity</h2>

                    <p className="mb-6">
                        Sarah wants to track when users view articles. She adds 3 lines of code:
                    </p>

                    <TerminalDemo
                        title="track_article_view.py"
                        mode="code"
                        code={`# Track when user views an article
await sw.track(
    user_id=42,
    entity_id="python-async-tutorial",
    action="view"
)

print("\u2705 Activity tracked!")`}
                        autoplay
                    />

                    <div className="my-8 border-l-4 border-green-500 bg-black p-6 rounded">
                        <p className="text-zinc-300 flex items-start gap-3 text-lg">
                            <CheckCircle2 className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                            <span>
                                That's it! Shadow Watch just recorded this activity, updated the user profile,
                                and started building a behavioral fingerprint.
                            </span>
                        </p>
                    </div>

                    {/* Anatomy of track() */}
                    <div id="anatomy" className="mt-12">
                        <h3 className="mb-6">Anatomy of track()</h3>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch explain track
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-6">
                                    <div>
                                        <div className="text-green-500 font-bold mb-2">user_id</div>
                                        <p className="text-zinc-300 mb-2">Who did this? Your app's user identifier.</p>
                                        <div className="font-mono text-sm text-zinc-500">
                                            user_id=42  <span className="text-zinc-600"># Integer</span><br />
                                            user_id="user_abc123"  <span className="text-zinc-600"># String</span><br />
                                            user_id=UUID("...")  <span className="text-zinc-600"># UUID</span>
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-green-500 font-bold mb-2">entity_id</div>
                                        <p className="text-zinc-300 mb-2">What did they interact with?</p>
                                        <div className="font-mono text-sm text-zinc-500">
                                            entity_id="python-async-tutorial"  <span className="text-zinc-600"># Article</span><br />
                                            entity_id="product_12345"  <span className="text-zinc-600"># Product</span><br />
                                            entity_id="AAPL"  <span className="text-zinc-600"># Stock</span>
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-green-500 font-bold mb-2">action</div>
                                        <p className="text-zinc-300 mb-2">What did they do?</p>
                                        <div className="font-mono text-sm text-zinc-500">
                                            action="view"  <span className="text-zinc-600"># Most common</span><br />
                                            action="click"<br />
                                            action="purchase"<br />
                                            action="add_to_cart"
                                        </div>
                                    </div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* What Happened */}
                <section id="what-happened" className="mb-16">
                    <h2 className="mb-8">What Just Happened Behind the Scenes?</h2>

                    <p className="mb-8">
                        When Sarah called <code>await sw.track(...)</code>,
                        Shadow Watch executed a 5-step pipeline in &lt;10ms:
                    </p>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch trace track
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-3 font-mono text-sm">
                                <div className="text-green-500">
                                    [1] Validation <span className="text-zinc-500">~1ms</span>
                                </div>
                                <div className="text-zinc-400 ml-4">
                                    Checked user_id, entity_id, action are valid
                                </div>

                                <div className="text-green-500 mt-2">
                                    [2] Event Storage <span className="text-zinc-500">~3ms</span>
                                </div>
                                <div className="text-zinc-400 ml-4">
                                    Wrote to user_activities table (UTC timestamp, microsecond precision)
                                </div>

                                <div className="text-green-500 mt-2">
                                    [3] Profile Update <span className="text-zinc-500">~4ms</span>
                                </div>
                                <div className="text-zinc-400 ml-4">
                                    Updated user_profiles: total_items++, recalculated entropy, refreshed fingerprint
                                </div>

                                <div className="text-green-500 mt-2">
                                    [4] Library Update <span className="text-zinc-500">~2ms</span>
                                </div>
                                <div className="text-zinc-400 ml-4">
                                    Added to interest_library: view_count++, updated last_viewed
                                </div>

                                <div className="text-green-500 mt-2">
                                    [5] Cache Sync <span className="text-zinc-500">~1ms</span>
                                </div>
                                <div className="text-zinc-400 ml-4">
                                    Synced to Redis (if configured)
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    {/* Data Flow */}
                    <div id="data-flow" className="mt-12">
                        <h3 className="mb-6">Visual Data Flow</h3>

                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="space-y-2 font-mono text-sm">
                                    <div className="text-zinc-400">
                                        → Your app calls <span className="text-green-500">sw.track(42, "python-async-tutorial", "view")</span>
                                    </div>
                                    <div className="text-zinc-400 ml-4">
                                        → Shadow Watch validates input
                                    </div>
                                    <div className="text-zinc-400 ml-8">
                                        → Writes to <span className="text-green-500">user_activities</span>
                                    </div>
                                    <div className="text-zinc-400 ml-8">
                                        → Updates <span className="text-green-500">user_profiles</span> (fingerprint, entropy)
                                    </div>
                                    <div className="text-zinc-400 ml-8">
                                        → Updates <span className="text-green-500">interest_library</span> (view_count++)
                                    </div>
                                    <div className="text-zinc-400 ml-8">
                                        → Syncs to Redis cache
                                    </div>
                                    <div className="text-green-500 ml-4 mt-2">
                                        ✓ Returns success
                                    </div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* Verification */}
                <section id="verification" className="mb-16">
                    <h2 className="mb-8">Step 3: Verify It Worked</h2>

                    <p className="mb-6">
                        Sarah wants proof. She checks the user's profile:
                    </p>

                    <CodeBlock
                        code={`# Get user's behavioral profile
profile = await sw.get_profile(user_id=42)
print(profile)`}
                        language="python"
                    />

                    <p className="my-6">Output:</p>

                    <CodeBlock
                        code={`{
  "user_id": 42,
  "total_items": 1,
  "fingerprint": "a3f2c1b4e5d6f7a8b9c0d1e2f3a4b5c6",
  "entropy": 0.0,
  "library": [
    {
      "entity_id": "python-async-tutorial",
      "view_count": 1,
      "last_viewed": "2026-01-13T09:00:00.123456Z",
      "score": 1.0,
      "pinned": false
    }
  ],
  "pin ned_count": 0,
  "created_at": "2026-01-13T09:00:00.100000Z",
  "updated_at": "2026-01-13T09:00:00.123456Z"
}`}
                        language="json"
                    />

                    <div className="mt-8">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch explain profile
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-4">
                                    <div>
                                        <div className="text-green-500 font-bold">fingerprint</div>
                                        <p className="text-zinc-400 text-sm">
                                            Unique hash of behavioral pattern. Changes as they interact more.
                                            Used to detect if login matches historical behavior.
                                        </p>
                                    </div>

                                    <div>
                                        <div className="text-yellow-500 font-bold">entropy</div>
                                        <p className="text-zinc-400 text-sm">
                                            Randomness vs. structure (0.0-1.0). Low = human-like. High = bot-like.
                                            Current: 0.0 (only 1 activity, no pattern yet).
                                        </p>
                                    </div>

                                    <div>
                                        <div className="text-green-500 font-bold">library</div>
                                        <p className="text-zinc-400 text-sm">
                                            Everything they've interacted with, ranked by importance (score).
                                            Think: "User 42's interests by engagement."
                                        </p>
                                    </div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* Success */}
                <div className="border-l-4 border-green-500 bg-black p-8 mb-16 rounded">
                    <div className="flex items-start gap-4">
                        <CheckCircle2 className="w-10 h-10 text-green-500 flex-shrink-0" />
                        <div>
                            <h3 className="text-2xl font-bold mb-4 text-green-500">Sarah Did It! (9:59 AM)</h3>
                            <p className="mb-4">
                                In <span className="text-green-500">4 minutes</span>, Sarah:
                            </p>
                            <ul className="space-y-2 font-mono text-zinc-400">
                                <li><span className="text-green-500">✓</span> Installed Shadow Watch</li>
                                <li><span className="text-green-500">✓</span> Created database tables</li>
                                <li><span className="text-green-500">✓</span> Tracked first activity</li>
                                <li><span className="text-green-500">✓</span> Retrieved behavioral profile</li>
                                <li><span className="text-green-500">✓</span> Understood how it works</li>
                            </ul>
                            <p className="mt-6 text-zinc-300">
                                At standup: <span className="text-green-500">"Already done. It's tracking behavioral patterns now."</span>
                            </p>
                        </div>
                    </div>
                </div>

                {/* Next Steps */}
                <section id="next-steps" className="mb-16">
                    <h2 className="mb-8">What's Next?</h2>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Link to="/docs/fastapi-integration" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                                    Production Integration
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    QuantForge integrated Shadow Watch into their trading platform.
                                    Middleware, trust scores, blocking attacks.
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/behavioral-intelligence" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                                    How It Works (Deep Dive)
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    Alice's story: Shadow Watch stopped an account takeover at 3 AM
                                    when traditional 2FA failed.
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/postgresql" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                                    Scale to Production
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    Move from SQLite to PostgreSQL + Redis. Handle millions of events per day.
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/core-concepts" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                                    Core Concepts
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    Understand fingerprints, entropy, trust scores, and profile evolution.
                                </p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
