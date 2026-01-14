import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const SocialMedia = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Social Media: Account Safety</h1>
                    <p className="text-xl text-zinc-400">
                        How ConnectApp protects 1M users from account takeovers
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            <span className="text-yellow-500">Challenge:</span> Phishing attacks steal credentials daily.
                            Traditional 2FA? Users disable it.
                        </p>
                        <p className="text-zinc-300 mt-3">
                            <span className="text-green-500">Solution:</span> Shadow Watch runs silently. No user friction.
                            Blocks takeovers before damage.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Track Social Activity</h2>

                    <CodeBlock
                        code={`# Track post views
await sw.track(
    user_id=user.id,
    entity_id=f"post_{post.id}",
    action="view",
    metadata={"author_id": post.author_id}
)

# Track profile visits
await sw.track(
    user_id=viewer.id,
    entity_id=f"profile_{profile_owner.id}",
    action="visit"
)

# Track friend requests
await sw.track(
    user_id=sender.id,
    entity_id=f"user_{recipient.id}",
    action="friend_request"
)`}
                        language="python"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Detect Account Takeover on Login</h3>

                    <CodeBlock
                        code={`@app.post("/login")
async def login(email: str, password: str, request: Request):
    user = await authenticate(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Check trust score
    trust = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.headers.get("x-device-id")
        }
    )
    
    if trust["action"] == "block":
        # Attacker detected
        await send_security_email(user.email, trust)
        await lock_account_temporarily(user.id)
        raise HTTPException(403, "Suspicious activity. Check your email.")
    
    return create_session(user)`}
                        language="python"
                        filename="auth.py"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Real Attack Blocked</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">!</span> Attacker Login Attempt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm">
                                <div className="text-zinc-300">User: sarah@example.com</div>
                                <div className="text-zinc-300">Time: 3:47 AM</div>
                                <div className="text-red-500">IP: 185.220.101.42 (Romania)</div>
                                <div className="text-red-500">Device: Windows + Firefox (Sarah uses macOS + Chrome)</div>
                                <div className="text-red-500">Pattern: Never seen before</div>
                                <div className="text-red-500 mt-3 font-bold">Trust Score: 0.19 → BLOCKED</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">✓</span> Sarah's Normal Login (Next Day)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm">
                                <div className="text-zinc-300">User: sarah@example.com</div>
                                <div className="text-zinc-300">Time: 9:15 AM</div>
                                <div className="text-green-500">IP: 192.168.1.100 (USA, Home)</div>
                                <div className="text-green-500">Device: macOS + Chrome (Matches history)</div>
                                <div className="text-green-500">Pattern: Consistent with profile</div>
                                <div className="text-green-500 mt-3 font-bold">Trust Score: 0.93 → ALLOWED</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Impact</h2>

                    <Terminal>
                        <TerminalBody mode="text">
                            <div className="space-y-3 font-mono text-sm">
                                <div className="text-green-500">✓ Account takeovers blocked: 1,247 (Month 1)</div>
                                <div className="text-green-500">✓ Users notified before damage: 100%</div>
                                <div className="text-green-500">✓ Support tickets: -67% (fewer compromised accounts)</div>
                                <div className="text-zinc-300 mt-3"># No user friction (runs silently)</div>
                                <div className="text-zinc-300"># Trust from users +24%</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>
            </article>
        </div>
    );
};
