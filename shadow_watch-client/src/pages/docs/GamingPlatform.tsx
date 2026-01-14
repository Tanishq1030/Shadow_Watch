import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const GamingPlatform = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Gaming Platform: Bot Detection</h1>
                    <p className="text-xl text-zinc-400">
                        How GameVerse stopped cheaters with Shadow Watch
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            <span className="text-red-500">Problem:</span> Bots farming in-game currency, ruining economy.
                            Traditional anti-cheat couldn't detect sophisticated bots.
                        </p>
                        <p className="text-zinc-300 mt-3">
                            <span className="text-green-500">Solution:</span> Shadow Watch's entropy engine detected mechanical patterns.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Track Player Actions</h2>

                    <CodeBlock
                        code={`# Track quest completion
await sw.track(
    user_id=player.id,
    entity_id="quest_dragon_slayer",
    action="quest_complete",
    metadata={
        "completion_time_seconds": 1847,
        "level": player.level,
        "rewards": {"gold": 1000, "xp": 5000}
    }
)

# Track item trades
await sw.track(
    user_id=player.id,
    entity_id="legendary_sword_001",
    action="trade",
    metadata={
        "trade_partner_id": other_player.id,
        "gold_value": 50000
    }
)`}
                        language="python"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Detect Bots by Entropy</h3>

                    <CodeBlock
                        code={`# On suspicious activity
profile = await sw.get_profile(player.id)

if profile["entropy"] > 0.85:
    # Bot-like behavior
    await flag_for_review(player.id, reason="high_entropy")
    
    # Humans show patterns (0.3-0.6 entropy)
    # Bots are too random or too mechanical (>0.8)`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Bot Detection Patterns</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-red-500">!</span> Bot Indicators (High Entropy)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm text-zinc-400">
                                <div>• Completes quests at exact intervals (every 30 min)</div>
                                <div>• Never revisits favorite NPCs</div>
                                <div>• Perfectly optimal path-finding</div>
                                <div>• Active 24/7 without breaks</div>
                                <div>• Farm routes in alphabetical order</div>
                                <div className="text-red-500 mt-3">Entropy: 0.94 → BAN</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">✓</span> Human Player (Normal Entropy)
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm text-zinc-400">
                                <div>• Irregular play sessions (2-4 hours)</div>
                                <div>• Revisits favorite zones</div>
                                <div>• Sometimes fails quests</div>
                                <div>• Active 6-10 PM most days</div>
                                <div>• Explores randomly</div>
                                <div className="text-green-500 mt-3">Entropy: 0.47 → ALLOWED</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Results</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> gameverse results --quarter 1
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-sm">
                                <div className="text-green-500">✓ Bots detected: 2,847</div>
                                <div className="text-green-500">✓ Accounts banned: 2,801</div>
                                <div className="text-yellow-500">⚠ False positives: 46 (appeals resolved)</div>
                                <div className="text-zinc-300 mt-3"># In-game economy stabilized</div>
                                <div className="text-zinc-300"># Player retention +18%</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>
            </article>
        </div >
    );
};
