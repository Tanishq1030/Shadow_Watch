import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const FingerprintVerification = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Fingerprint Verification</h1>
                    <p className="text-xl text-zinc-400">
                        How Shadow Watch detects anomalies in real-time
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            A <span className="text-green-500">fingerprint</span> is a hash of behavioral patterns.
                            When someone logs in, Shadow Watch compares their current behavior to the stored fingerprint.
                            Mismatch? Potential attacker.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">How Fingerprints are Generated</h2>

                    <CodeBlock
                        code={`import hashlib
from typing import Dict, List

def generate_fingerprint(
    interests: Dict[str, int],
    temporal_patterns: List[int],
    interaction_frequencies: Dict[str, float]
) -> str:
    """Generate behavioral fingerprint"""
    
    # Combine all behavioral data
    data_string = (
        str(sorted(interests.items())) +
        str(temporal_patterns) +
        str(sorted(interaction_frequencies.items()))
    )
    
    # Hash to create fingerprint
    fingerprint = hashlib.sha256(data_string.encode()).hexdigest()
    
    return fingerprint

# Example user
fingerprint = generate_fingerprint(
    interests={"Python": 80, "JavaScript": 15, "Ruby": 5},
    temporal_patterns=[9, 10, 11, 12, 13, 14, 15, 16, 17],  # 9-5 PM
    interaction_frequencies={"react": 0.5, "vue": 0.3, "angular": 0.2}
)

print(fingerprint)
# f4a3b2c1e5d6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2`}
                        language="python"
                        filename="fingerprint_generator.py"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Verification Process</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch verify --user 42
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-3">
                                <div>
                                    <div className="text-zinc-400">Step 1: Fetch stored fingerprint</div>
                                    <div className="text-green-500">f4a3b2c1e5d6...</div>
                                </div>

                                <div>
                                    <div className="text-zinc-400">Step 2: Generate current fingerprint from recent activity</div>
                                    <div className="text-green-500">f4a3b2c1e5d6... <span className="text-zinc-500">(MATCH)</span></div>
                                </div>

                                <div>
                                    <div className="text-zinc-400">Step 3: Compare context</div>
                                    <div className="text-green-500">IP: USA → USA ✓</div>
                                    <div className="text-green-500">Device: macOS → macOS ✓</div>
                                    <div className="text-green-500">Time: 10 AM → Normal ✓</div>
                                </div>

                                <div className="text-green-500 font-bold mt-2">
                                    Result: VERIFIED (Trust Score: 0.94)
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Anomaly Detection</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">!</span> Attacker Detected
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-3">
                                <div>
                                    <div className="text-zinc-400">Step 1: Fetch stored fingerprint</div>
                                    <div className="text-green-500">f4a3b2c1e5d6... <span className="text-zinc-500">(User's normal)</span></div>
                                </div>

                                <div>
                                    <div className="text-zinc-400">Step 2: Generate current fingerprint</div>
                                    <div className="text-red-500">a1b2c3d4e5f6... <span className="text-zinc-500">(DIFFERENT!)</span></div>
                                </div>

                                <div>
                                    <div className="text-zinc-400">Step 3: Compare context</div>
                                    <div className="text-red-500">IP: USA → Romania ✗</div>
                                    <div className="text-red-500">Device: macOS → Windows ✗</div>
                                    <div className="text-red-500">Time: 3 AM → Unusual ✗</div>
                                </div>

                                <div className="text-red-500 font-bold mt-2">
                                    Result: ANOMALY DETECTED (Trust Score: 0.21) → BLOCK
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Fingerprint Evolution</h2>

                    <p className="mb-4">Fingerprints adapt to legitimate user changes:</p>

                    <CodeBlock
                        code={`def update_fingerprint(
    old_fingerprint: str,
    new_activity: Dict,
    weight: float = 0.1  # How much new activity affects fingerprint
) -> str:
    """Graduallyupdate fingerprint with new behavior"""
    
    # Combine old and new data (weighted average)
    old_data = deserialize_fingerprint(old_fingerprint)
    blended_data = blend_behavioral_data(old_data, new_activity, weight)
    
    # Generate new fingerprint
    return generate_fingerprint(blended_data)

# User starts learning JavaScript after being Python-only
# Fingerprint gradually shifts to reflect this
# Old: {"Python": 100}
# Week 1: {"Python": 95, "JavaScript": 5}
# Week 4: {"Python": 80, "JavaScript": 20}
# Week 12: {"Python": 60, "JavaScript": 40}`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Implementation</h2>

                    <CodeBlock
                        code={`@app.post("/login")
async def login(email: str, password: str, request: Request):
    user = await authenticate(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Verify fingerprint
    verification = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.headers.get("x-device-id")
        }
    )
    
    # Check factors
    if verification["factors"]["fingerprint_match"] < 0.5:
        # Fingerprint mismatch - likely attacker
        await block_login(user.id, "fingerprint_mismatch")
        raise HTTPException(403, "Suspicious activity detected")
    
    return create_session(user)`}
                        language="python"
                    />
                </section>
            </article>
        </div>
    );
};
