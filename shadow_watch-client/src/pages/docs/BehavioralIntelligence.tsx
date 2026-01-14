import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const BehavioralIntelligence = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="mb-12">
                    <h1 className="mb-4">
                        What is Behavioral Intelligence?
                    </h1>
                    <p className="text-xl text-zinc-400">
                        How Alice's account was saved from a sophisticated attack
                    </p>
                </div>

                {/* Alice's Story */}
                <section id="alice-story" className="mb-12">
                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> cat alice_story.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-4 text-zinc-300">
                                <p>
                                    Alice was a software engineer at a Fortune 500 company.
                                    Her GitHub account had <span className="text-green-500">2FA enabled</span>.
                                    Her password was <span className="text-green-500">unique and 24 characters long</span>.
                                </p>
                                <p>
                                    But at <span className="text-red-500">3 AM on a Tuesday</span>, someone logged into her account
                                    from <span className="text-red-500">a new device in a different country</span>.
                                </p>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <div className="grid md:grid-cols-2 gap-6 mt-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">✓</span> Traditional Auth Said
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="font-mono text-sm space-y-1">
                                    <div className="text-green-500">✓ Password: Correct</div>
                                    <div className="text-green-500">✓ 2FA Code: Valid</div>
                                    <div className="text-green-500">✓ Session: Authenticated</div>
                                    <div className="text-zinc-500 mt-3"># "Everything checks out. Access granted."</div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-red-500">✗</span> Shadow Watch Said
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="font-mono text-sm space-y-1">
                                    <div className="text-red-500">⚠ Login time: Anomalous</div>
                                    <div className="text-red-500">⚠ Location: New country</div>
                                    <div className="text-red-500">⚠ Device: Never seen</div>
                                    <div className="text-red-500">⚠ Pattern: Mismatch</div>
                                    <div className="text-zinc-500 mt-3"># "This doesn't look like Alice..."</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* The Problem */}
                <section id="the-problem" className="mb-12">
                    <h2 className="mb-6">The Problem with Traditional Auth</h2>

                    <p className="mb-6">
                        Traditional authentication only answers one question: <strong>"Do you have the right credentials?"</strong>
                    </p>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> cat traditional_auth_checks.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm">
                                <div className="text-zinc-300">1. Do you know the password? <span className="text-zinc-500">(Knowledge)</span></div>
                                <div className="text-zinc-300">2. Do you have the 2FA device? <span className="text-zinc-500">(Possession)</span></div>
                                <div className="text-zinc-300">3. Are you this person? <span className="text-zinc-500">(Biometrics - sometimes)</span></div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">$</span> cat traditional_auth_MISSING.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm">
                                <div className="text-red-500">❌ Does this behavior match the user?</div>
                                <div className="text-red-500">❌ Is this login pattern normal?</div>
                                <div className="text-red-500">❌ Would this user be accessing at 3 AM?</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                {/* How It Works */}
                <section id="how-it-works" className="mb-12">
                    <h2 className="mb-6">How Behavioral Intelligence Works</h2>

                    <p className="mb-8">
                        Behavioral intelligence adds a fourth dimension: <strong className="text-green-500">"Does this ACT like the real user?"</strong>
                    </p>

                    <div className="space-y-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch observe --step 1
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-4">
                                    <p className="font-bold text-white">Step 1: Silent Observation</p>
                                    <p className="text-zinc-300">
                                        Shadow Watch tracks user activity without interfering:
                                    </p>
                                    <CodeBlock
                                        code={`# When Alice views a repository
await sw.track(
    user_id=alice.id,
    entity_id="react/react",
    action="view_repository"
)

# When Alice stars a project
await sw.track(
    user_id=alice.id,
    entity_id="facebook/react",
    action="star",
    metadata={"language": "JavaScript"}
)`}
                                        language="python"
                                    />
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch analyze --step 2
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-4">
                                    <p className="font-bold text-white">Step 2: Pattern Recognition</p>
                                    <p className="text-zinc-300">Over time, Shadow Watch learns:</p>
                                    <div className="font-mono text-sm space-y-1 text-zinc-400">
                                        <div>• Alice views Python repositories 80% of the time</div>
                                        <div>• She logins between 9 AM - 6 PM ET</div>
                                        <div>• Her typical session lasts 2-4 hours</div>
                                        <div>• She uses macOS Chrome 90% of the time</div>
                                    </div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">$</span> shadowwatch fingerprint --step 3
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="space-y-4">
                                    <p className="font-bold text-white">Step 3: Behavioral Fingerprint</p>
                                    <p className="text-zinc-300">A unique fingerprint is generated from her activity:</p>
                                    <div className="font-mono text-sm text-green-500 mt-2">
                                        Fingerprint: sha256(interests + patterns + entropy)<br />
                                        → f4a3b2c1...  <span className="text-zinc-500"># Unique to Alice's behavior</span>
                                    </div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* What's Tracked */}
                <section id="what-tracked" className="mb-12">
                    <h2 className="mb-6">What Shadow Watch Tracks</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch explain --tracked-data
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="grid md:grid-cols-2 gap-8 font-mono text-sm">
                                <div>
                                    <div className="text-white font-bold mb-2">Activity Data:</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>• What entities they interact with</div>
                                        <div>• Frequency of interactions</div>
                                        <div>•  Time-of-day patterns</div>
                                        <div>• Session duration</div>
                                        <div>• Navigation paths</div>
                                    </div>
                                </div>

                                <div>
                                    <div className="text-white font-bold mb-2">Context Data:</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>• Device fingerprints</div>
                                        <div>• Geographic location</div>
                                        <div>• IP addresses</div>
                                        <div>• User agents</div>
                                        <div>• Login times</div>
                                    </div>
                                </div>

                                <div>
                                    <div className="text-white font-bold mb-2">Pattern Data:</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>• Interest clusters</div>
                                        <div>• Behavioral entropy</div>
                                        <div>• Velocity checks</div>
                                        <div>• Anomaly scores</div>
                                        <div>• Historical baselines</div>
                                    </div>
                                </div>

                                <div>
                                    <div className="text-red-500 font-bold mb-2">NOT Tracked:</div>
                                    <div className="space-y-1 text-zinc-600 line-through">
                                        <div>• Passwords or credentials</div>
                                        <div>• Personal messages/content</div>
                                        <div>• Keystrokes</div>
                                        <div>• Screenshots</div>
                                        <div>• Biometric data</div>
                                    </div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                {/* Trust Score */}
                <section id="trust-score" className="mb-12">
                    <h2 className="mb-6">Trust Score Calculation</h2>

                    <p className="mb-6">
                        When Alice (or an attacker) attempts to log in, Shadow Watch calculates a trust score:
                    </p>

                    <CodeBlock
                        code={`trust_result = await sw.verify_login(
    user_id=alice.id,
    request_context={
        "ip": "203.0.113.42",
        "country": "Romania",  # Alice is usually in USA
        "user_agent": "Windows Firefox",  # Alice uses macOS Chrome
        "timestamp": datetime(2024, 1, 16, 3, 0, 0),  # 3 AM
        "library_fingerprint": "abc123..."  # Doesn't match Alice's
    }
)

# Result:
{
    "trust_score": 0.23,  # Very low (0.0 - 1.0 scale)
    "risk_level": "high",
    "action": "block",
    "factors": {
        "location_anomaly": -0.4,
        "time_anomaly": -0.3,
        "device_mismatch": -0.2,
        "behavioral_mismatch": -0.5
    }
}`}
                        language="python"
                        filename="trust_score_example.py"
                    />
                </section>

                {/* Real Impact */}
                <section id="real-impact" className="mb-12">
                    <h2 className="mb-6">Real-World Impact</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> cat alice_outcome.txt
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-4">
                                <p className="font-bold text-green-500">Attack Blocked!</p>
                                <p className="text-zinc-300">
                                    The 3 AM login attempt was <span className="text-red-500">automatically blocked</span>.
                                    Alice received an email: <span className="text-green-500">"Suspicious login attempt blocked."</span>
                                </p>
                                <p className="text-zinc-300">
                                    The next morning, Alice checked. Someone had stolen her 2FA backup codes during a phishing attack.
                                    They had her password. They had her 2FA. But they <strong className="text-white">didn't have her behavioral patterns</strong>.
                                </p>
                                <p className="text-zinc-300">
                                    Traditional auth would have let them in. Behavioral intelligence saved her account.
                                </p>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <div className="grid md:grid-cols-3 gap-4 mt-6">
                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-red-500 mb-2">0.23</div>
                                    <div className="text-sm text-zinc-400">Attacker's trust score</div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-green-500 mb-2">0.94</div>
                                    <div className="text-sm text-zinc-400">Alice's normal trust score</div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalBody mode="text">
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-red-500 mb-2">BLOCKED</div>
                                    <div className="text-sm text-zinc-400">Attacker's access</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                {/* Next Steps */}
                <section className="mb-12">
                    <h2 className="mb-6">Next Steps</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <Link to="/docs/getting-started" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                                    Get Started
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    Integrate Shadow Watch in 5 minutes
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/core-concepts" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                                    Core Concepts
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    Deep dive into fingerprints and trust scores
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/entropy-engine" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                                    Entropy Engine
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    The math behind behavioral intelligence
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/fastapi-integration" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                                    FastAPI Integration
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-zinc-400">
                                    See a complete production example
                                </p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
