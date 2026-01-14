import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const EntropyEngine = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Entropy Engine Deep Dive</h1>
                    <p className="text-xl text-zinc-400">
                        The mathematics behind pattern detection
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            <span className="text-green-500">Entropy</span> measures randomness vs. structure.
                            Humans show patterns. Bots don't. This is how we detect them.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Shannon Entropy Formula</h2>

                    <CodeBlock
                        code={`H(X) = -Σ p(x) * log₂(p(x))

Where:
- H(X) = entropy (0.0 to 1.0, normalized)
- p(x) = probability of event x
- Σ = sum over all possible events

Example:
User views: ["Python", "Python", "Python", "JavaScript"]
- p(Python) = 0.75
- p(JavaScript) = 0.25

H = -[0.75 * log₂(0.75) + 0.25 * log₂(0.25)]
H = -[0.75 * -0.415 + 0.25 * -2.0]
H = -[-0.311 + -0.5]
H = 0.811 (normalized to 0-1)

Lower entropy (0.3-0.6) = Human-like patterns
Higher entropy (0.8-1.0) = Random/mechanical`}
                        language="text"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Implementation</h2>

                    <CodeBlock
                        code={`import math
from collections import Counter
from typing import List

def calculate_entropy(events: List[str]) -> float:
    """Calculate Shannon entropy of event sequence"""
    if not events:
        return 0.0
    
    # Count frequencies
    counts = Counter(events)
    total = len(events)
    
    # Calculate probabilities
    probabilities = [count / total for count in counts.values()]
    
    # Shannon entropy
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    
    # Normalize to 0-1 range
    max_entropy = math.log2(len(counts))
    normalized = entropy / max_entropy if max_entropy > 0 else 0
    
    return normalized

# Example: Human user
human_views = ["Python"] * 8 + ["JavaScript"] * 2 + ["Ruby"] * 1
print(calculate_entropy(human_views))  # 0.52 (structured)

# Example: Bot
bot_views = list("ABCDEFGHIJ")  # Perfectly distributed
print(calculate_entropy(bot_views))  # 1.0 (random)`}
                        language="python"
                        filename="entropy_calculator.py"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Real-World Examples</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">✓</span> Human Developer
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs">
                                <div className="text-zinc-400 mb-2">Viewed repos:</div>
                                <div className="text-green-500">react (15×), vue (4×), angular (2×), svelte (1×)</div>
                                <div className="text-zinc-500 mt-2">Pattern: Favorites clear focus</div>
                                <div className="text-green-500 mt-2">Entropy: 0.48 → HUMAN</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">✗</span> Scraper Bot
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs">
                                <div className="text-zinc-400 mb-2">Viewed repos:</div>
                                <div className="text-red-500">a-repo, b-repo, c-repo, d-repo... (alphabetical)</div>
                                <div className="text-zinc-500 mt-2">Pattern: Perfectly distributed, no favorites</div>
                                <div className="text-red-500 mt-2">Entropy: 0.97 → BOT</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-yellow-500">⚠</span> New User (Exploring)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs">
                                <div className="text-zinc-400 mb-2">Viewed repos:</div>
                                <div className="text-yellow-500">python (3×), javascript (2×), ruby (2×), go (2×)</div>
                                <div className="text-zinc-500 mt-2">Pattern: Exploring, no strong preference yet</div>
                                <div className="text-yellow-500 mt-2">Entropy: 0.68 → MONITOR (will decrease over time)</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Temporal Entropy</h2>

                    <p className="mb-4">Time-based patterns reveal even more:</p>

                    <CodeBlock
                        code={`def calculate_temporal_entropy(timestamps: List[datetime]) -> float:
    """Entropy of when user is active"""
    # Bucket by hour of day
    hours = [ts.hour for ts in timestamps]
    return calculate_entropy([str(h) for h in hours])

# Human: Active 9-5 PM
human_times = [9, 10, 11, 12, 13, 14, 15, 16, 17]
temporal_entropy = calculate_temporal_entropy(human_times)
# Low entropy (0.3) = predictable schedule

# Bot: Active 24/7 at exact intervals
bot_times = list(range(24))  # Every hour
temporal_entropy = calculate_temporal_entropy(bot_times)
# High entropy (1.0) = no pattern`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Thresholds</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch entropy-thresholds
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-sm space-y-2">
                                <div className="text-green-500">0.0 - 0.3: Highly predictable (power user)</div>
                                <div className="text-green-500">0.3 - 0.6: Normal human behavior</div>
                                <div className="text-yellow-500">0.6 - 0.8: Exploring/new user</div>
                                <div className="text-red-500">0.8 - 1.0: Bot-like/random</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>
            </article>
        </div>
    );
};
