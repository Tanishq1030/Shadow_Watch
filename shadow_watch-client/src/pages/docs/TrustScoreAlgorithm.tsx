import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const TrustScoreAlgorithm = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Trust Score Algorithm</h1>
                    <p className="text-xl text-zinc-400">
                        How Shadow Watch calculates trust in milliseconds
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            Trust score = <span className="text-green-500">weighted combination of 5 factors</span>.
                            Each factor contributes to final score (0.0-1.0).
                            Calculated in ~15ms.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">The Algorithm</h2>

                    <CodeBlock
                        code={`def calculate_trust_score(
    fingerprint_match: float,      # 0.0-1.0
    location_consistency: float,   # 0.0-1.0
    time_pattern_match: float,     # 0.0-1.0
    velocity_check: float,         # 0.0-1.0
    device_familiarity: float      # 0.0-1.0
) -> float:
    """Calculate overall trust score"""
    
    # Weighted average
    weights = {
        'fingerprint': 0.35,    # Highest weight
        'location': 0.25,
        'time': 0.20,
        'velocity': 0.10,
        'device': 0.10
    }
    
    trust_score = (
        fingerprint_match * weights['fingerprint'] +
        location_consistency * weights['location'] +
        time_pattern_match * weights['time'] +
        velocity_check * weights['velocity'] +
        device_familiarity * weights['device']
    )
    
    return trust_score

# Example: Normal login
score = calculate_trust_score(
    fingerprint_match=0.92,
    location_consistency=0.95,
    time_pattern_match=0.88,
    velocity_check=1.0,
    device_familiarity=0.85
)
print(score)  # 0.91 → HIGH TRUST → ALLOW`}
                        language="python"
                        filename="trust_score.py"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Factor Breakdown</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">1.</span> Fingerprint Match (35% weight)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>Compare current behavioral fingerprint to stored one</div>
                                <div className="text-green-500">Identical: 1.0</div>
                                <div className="text-yellow-500">Similar: 0.6-0.9</div>
                                <div className="text-red-500">Different: 0.0-0.5</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">2.</span> Location Consistency (25% weight)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>Is this IP/country normal for this user?</div>
                                <div className="text-green-500">Same city: 1.0</div>
                                <div className="text-yellow-500">Same country: 0.7</div>
                                <div className="text-red-500">Different continent: 0.2</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">3.</span> Time Pattern Match (20% weight)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>Does login time match user's schedule?</div>
                                <div className="text-green-500">Within typical hours: 1.0</div>
                                <div className="text-yellow-500">Off-hours but plausible: 0.6</div>
                                <div className="text-red-500">3 AM (user is 9-5): 0.1</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">4.</span> Velocity Check (10% weight)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>Could user physically travel between locations?</div>
                                <div className="text-green-500">Plausible: 1.0</div>
                                <div className="text-red-500">NY → Tokyo in 1 hour: 0.0</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">5.</span> Device Familiarity (10% weight)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>Have we seen this device/browser before?</div>
                                <div className="text-green-500">Known device: 1.0</div>
                                <div className="text-yellow-500">New device, same OS: 0.6</div>
                                <div className="text-red-500">Never seen: 0.3</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Decision Thresholds</h2>

                    <Terminal>
                        <TerminalBody mode="text">
                            <div className="font-mono text-sm space-y-2">
                                <div className="text-green-500">0.8 - 1.0: <strong>ALLOW</strong> (High trust, proceed normally)</div>
                                <div className="text-yellow-500">0.6 - 0.8: <strong>MONITOR</strong> (Medium trust, log for review)</div>
                                <div className="text-yellow-500">0.3 - 0.6: <strong>MFA</strong> (Low trust, require 2FA)</div>
                                <div className="text-red-500">0.0 - 0.3: <strong>BLOCK</strong> (Very low trust, deny access)</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Real Examples</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">✓</span> Normal Login
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-1">
                                <div>Fingerprint: 0.92</div>
                                <div>Location: 0.95</div>
                                <div>Time: 0.88</div>
                                <div>Velocity: 1.0</div>
                                <div>Device: 0.85</div>
                                <div className="text-green-500 font-bold mt-2">Trust Score: 0.91 → ALLOW</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-yellow-500">⚠</span> Suspicious (Require MFA)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-1">
                                <div>Fingerprint: 0.78</div>
                                <div className="text-yellow-500">Location: 0.45 (new country)</div>
                                <div>Time: 0.82</div>
                                <div>Velocity: 0.95</div>
                                <div className="text-yellow-500">Device: 0.35 (new device)</div>
                                <div className="text-yellow-500 font-bold mt-2">Trust Score: 0.58 → MFA REQUIRED</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">✗</span> Attacker
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-1">
                                <div className="text-red-500">Fingerprint: 0.15 (completely different behavior)</div>
                                <div className="text-red-500">Location: 0.10 (Romania, user in USA)</div>
                                <div className="text-red-500">Time: 0.20 (3 AM, user is 9-5)</div>
                                <div className="text-red-500">Velocity: 0.05 (impossible travel)</div>
                                <div className="text-red-500">Device: 0.10 (never seen)</div>
                                <div className="text-red-500 font-bold mt-2">Trust Score: 0.12 → BLOCKED</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Implementation in Production</h2>

                    <CodeBlock
                        code={`@app.post("/login")
async def protected_login(email: str, password: str, request: Request):
    user = await authenticate(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Calculate trust score
    trust_result = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.headers.get("x-device-id")
        }
    )
    
    # Act on trust score
    if trust_result["action"] == "block":
        await log_security_event("login_blocked", user.id, trust_result)
        raise HTTPException(403, "Suspicious activity")
    
    elif trust_result["action"] == "require_mfa":
        return {"status": "mfa_required", "trust_score": trust_result["trust_score"]}
    
    # Allow login
    return create_session(user, trust_score=trust_result["trust_score"])`}
                        language="python"
                        filename="protected_login.py"
                    />
                </section>
            </article>
        </div>
    );
};
