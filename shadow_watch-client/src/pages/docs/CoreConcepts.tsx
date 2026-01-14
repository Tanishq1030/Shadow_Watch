import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const CoreConcepts = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Core Concepts</h1>
                    <p className="text-xl text-zinc-400">
                        Understanding the fingerprint that evolves with your users
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            Your users aren't static. They upgrade phones, get new laptops, move apartments.
                            Shadow Watch's fingerprint <span className="text-green-500">evolves with them</span>—but
                            still catches impostors. How?
                        </p>
                    </TerminalBody>
                </Terminal>

                <section id="activity-tracking" className="mb-12">
                    <h2 className="mb-6">Activity Tracking</h2>

                    <p className="mb-6">
                        Shadow Watch tracks user interactions silently. Every action builds the behavioral profile.
                    </p>

                    <CodeBlock
                        code={`await sw.track(
    user_id=123,
    entity_id="python-tutorial",
    action="view",
    metadata={"source": "search", "duration_seconds": 450}
)`}
                        language="python"
                    />

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch explain parameters
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="grid md:grid-cols-3 gap-4 font-mono text-sm">
                                <div>
                                    <div className="text-green-500 font-bold mb-1">user_id</div>
                                    <div className="text-zinc-400">Unique identifier</div>
                                </div>
                                <div>
                                    <div className="text-green-500 font-bold mb-1">entity_id</div>
                                    <div className="text-zinc-400">What they interacted with</div>
                                </div>
                                <div>
                                    <div className="text-green-500 font-bold mb-1">action</div>
                                    <div className="text-zinc-400">Type of interaction</div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalBody mode="text">
                            <p className="text-sm text-zinc-400">
                                <span className="text-yellow-500">Best Practice:</span> Track everything that reveals user intent: views, searches,
                                clicks, purchases, logins. The more data, the better the fingerprint.
                            </p>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="fingerprinting" className="mb-12">
                    <h2 className="mb-6">Behavioral Fingerprinting</h2>

                    <p className="mb-6">
                        A fingerprint is generated from the user's unique behavioral pattern:
                    </p>

                    <CodeBlock
                        code={`fingerprint = hash(
    interest_distribution +
    temporal_patterns +
    interaction_frequencies +
    entity_relationships
)`}
                        language="python"
                    />

                    <div className="space-y-4 mt-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">→</span> Interest Distribution
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <p className="text-sm text-zinc-300">
                                    What percentage of activities fall into each category?
                                </p>
                                <p className="text-sm text-zinc-500 mt-2">Example: 60% Python, 30% JavaScript, 10% Ruby</p>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">→</span> Temporal Patterns
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <p className="text-sm text-zinc-300">
                                    When are they active? How long are sessions?
                                </p>
                                <p className="text-sm text-zinc-500 mt-2">Example: 9 AM - 6 PM weekdays, 2-hour sessions</p>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">→</span> Interaction Frequencies
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <p className="text-sm text-zinc-300">
                                    How often do they interact with specific entities?
                                </p>
                                <p className="text-sm text-zinc-500 mt-2">Example: Views "react" repo 5x/week consistently</p>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                <section id="trust-score" className="mb-12">
                    <h2 className="mb-6">Trust Score Calculation</h2>

                    <p className="mb-6">
                        When a user logs in, Shadow Watch calculates a trust score from 0.0 (complete mismatch) to 1.0 (perfect match):
                    </p>

                    <CodeBlock
                        code={`result = await sw.verify_login(
    user_id=123,
    request_context={
        "ip": "192.0.2.1",
        "country": "USA",
        "user_agent": "Chrome/120.0 (macOS)",
        "device_fingerprint": "abc123...",
        "library_fingerprint": "def456...",
        "timestamp": datetime.now()
    }
)

# Returns:
{
    "trust_score": 0.89,          # High confidence
    "risk_level": "low",
    "action": "allow",
    "factors": {
        "fingerprint_match": 0.92,
        "location_consistency": 0.95,
        "time_pattern_match": 0.88,
        "velocity_check": 1.0,
        "device_familiarity": 0.85
    }
}`}
                        language="python"
                    />

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch thresholds
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="grid grid-cols-4 gap-2 font-mono text-xs">
                                <div className="text-center">
                                    <div className="text-green-500 font-bold">0.8-1.0</div>
                                    <div className="text-zinc-500">Allow</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-yellow-500 font-bold">0.6-0.8</div>
                                    <div className="text-zinc-500">Monitor</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-yellow-500 font-bold">0.3-0.6</div>
                                    <div className="text-zinc-500">MFA</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-red-500 font-bold">0.0-0.3</div>
                                    <div className="text-zinc-500">Block</div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section id="entropy" className="mb-12">
                    <h2 className="mb-6">Entropy Engine</h2>

                    <p className="mb-6">
                        Entropy measures the "chaos" vs. "pattern" in user behavior. High entropy = random/bot-like. Low entropy = predictable patterns.
                    </p>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">✓</span> Human Behavior
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <p className="text-sm mb-3">Patterns emerge naturally:</p>
                                <div className="space-y-1 text-sm text-zinc-400">
                                    <div>• 80% Python, 15% JS, 5% others</div>
                                    <div>• Active 9 AM - 5 PM consistently</div>
                                    <div>• Revisits favorite repos often</div>
                                    <div>• Sessions 2-4 hours</div>
                                </div>
                                <div className="mt-4 font-mono text-xs text-green-500">
                                    Entropy: 0.42 (structured)
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-red-500">✗</span> Bot Behavior
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <p className="text-sm mb-3">Perfectly random or mechanical:</p>
                                <div className="space-y-1 text-sm text-zinc-400">
                                    <div>• Views repos alphabetically</div>
                                    <div>• Active 24/7 at exact intervals</div>
                                    <div>• Never revisits anything</div>
                                    <div>• Sessions exactly 60 seconds</div>
                                </div>
                                <div className="mt-4 font-mono text-xs text-red-500">
                                    Entropy: 0.98 (chaotic)
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>

                <section id="profile-evolution" className="mb-12">
                    <h2 className="mb-6">Profile Evolution</h2>

                    <p className="mb-6">
                        The magic: profiles adapt to legitimate changes while rejecting attackers.
                    </p>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch timeline --days 90
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-4 font-mono text-sm">
                                <div>
                                    <div className="text-green-500 font-bold mb-1">Day 1-30</div>
                                    <div className="text-zinc-400">User views mostly Python repos. Profile establishes baseline fingerprint.</div>
                                </div>
                                <div>
                                    <div className="text-green-500 font-bold mb-1">Day 31-60</div>
                                    <div className="text-zinc-400">User starts learning JavaScript. Profile gradually incorporates new interests. Trust score stays high.</div>
                                </div>
                                <div>
                                    <div className="text-green-500 font-bold mb-1">Day 61-90</div>
                                    <div className="text-zinc-400">User upgrades from MacBook to Windows desktop. Device changes, but behavioral patterns persist. Shadow Watch recognizes same user, different device.</div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">!</span> What Triggers Alerts?
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <p className="text-sm mb-3">Sudden, drastic changes that don't match the evolution pattern:</p>
                            <div className="space-y-1 text-sm text-zinc-400">
                                <div>• Python-only user suddenly only views crypto repos (suspicious interest shift)</div>
                                <div>• Login from new country without travel history (location anomaly)</div>
                                <div>• 3 AM activity when user is always 9-5 (time anomaly)</div>
                                <div>• Machine-like precision in clicks (entropy spike)</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Next Steps</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <Link to="/docs/entropy-engine" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Entropy Engine Deep Dive
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    The mathematics behind pattern detection
                                </p>
                            </div>
                        </Link>

                        <Link to="/docs/trust-score" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Trust Score Algorithm
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">
                                    How trust scores are calculated in real-time
                                </p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
