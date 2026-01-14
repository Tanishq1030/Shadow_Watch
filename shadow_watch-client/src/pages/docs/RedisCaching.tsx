import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const RedisCaching = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Redis Caching</h1>
                    <p className="text-xl text-zinc-400">
                        Multi-instance deployments with shared cache
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            <span className="text-yellow-500">Why Redis?</span> When you scale Shadow Watch to multiple instances
                            (Kubernetes, serverless), each instance needs <span className="text-green-500">shared state</span>.
                            Redis provides nanosecond lookups across all instances.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Installation</h2>

                    <CodeBlock
                        code={`# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis  # macOS

# Test connection
redis-cli ping
# Response: PONG`}
                        language="bash"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Docker Compose</h3>

                    <CodeBlock
                        code={`version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:`}
                        filename="docker-compose.yml"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Configure Shadow Watch</h2>

                    <CodeBlock
                        code={`from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql+asyncpg://...",
    license_key="SW-TRIAL-...",
    redis_url="redis://localhost:6379"  # ← Add this!
)

# That's it! Shadow Watch will now:
# 1. Cache user profiles in Redis
# 2. Share cached state across all instances
# 3. Invalidate cache when profiles update`}
                        language="python"
                    />

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch cache-status
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-sm space-y-1">
                                <div className="text-green-500">✓ Redis connected: localhost:6379</div>
                                <div className="text-zinc-400">Cache hit rate: 87%</div>
                                <div className="text-zinc-400">Profile lookups: 5ms → 0.5ms</div>
                                <div className="text-zinc-400">Keys stored: 10,847</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Production Configuration</h2>

                    <h3 className="text-xl font-bold mb-4">Redis Cloud (Recommended)</h3>

                    <CodeBlock
                        code={`# Upstash (Serverless Redis)
REDIS_URL=rediss://default:abc123@us1-alert-firefly-12345.upstash.io:6379

# Redis Cloud
REDIS_URL=redis://default:password@redis-12345.c1.us-east-1-1.ec2.cloud.redislabs.com:12345

# AWS ElastiCache
REDIS_URL=redis://shadowwatch.abc123.use1.cache.amazonaws.com:6379`}
                        filename=".env.production"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">redis.conf Optimizations</h3>

                    <CodeBlock
                        code={`# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru  # Evict least recently used

# Persistence
save 900 1      # Save if 1 change in 15 min
save 300 10     # Save if 10 changes in 5 min
save 60 10000   # Save if 10K changes in 1 min

appendonly yes  # AOF persistence for durability

# Performance
tcp-backlog 511
timeout 300`}
                        filename="redis.conf"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Monitoring</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> redis-cli info stats
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs text-zinc-400 space-y-1">
                                <div>total_commands_processed: 1,247,853</div>
                                <div>keyspace_hits: 1,087,234</div>
                                <div>keyspace_misses: 160,619</div>
                                <div className="text-green-500 mt-2">hit_rate: 87%</div>
                                <div>used_memory_human: 187.3M</div>
                                <div>connected_clients: 23</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Performance Impact</h2>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Terminal>
                            <TerminalHeader>
                                <span className="text-yellow-500">Without Redis</span>
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="font-mono text-sm space-y-2">
                                    <div className="text-zinc-400">Profile lookup: 20ms</div>
                                    <div className="text-zinc-400">DB queries: 100%</div>
                                    <div className="text-zinc-400">Requests/sec: 500</div>
                                    <div className="text-red-500">Multi-instance: Inconsistent</div>
                                </div>
                            </TerminalBody>
                        </Terminal>

                        <Terminal>
                            <TerminalHeader>
                                <span className="text-green-500">✓ With Redis</span>
                            </TerminalHeader>
                            <TerminalBody mode="text">
                                <div className="font-mono text-sm space-y-2">
                                    <div className="text-green-500">Profile lookup: 0.5ms (40x faster)</div>
                                    <div className="text-green-500">DB queries: 13% (87% cache hit)</div>
                                    <div className="text-green-500">Requests/sec: 5,000</div>
                                    <div className="text-green-500">Multi-instance: Perfectly synced</div>
                                </div>
                            </TerminalBody>
                        </Terminal>
                    </div>
                </section>
            </article>
        </div>
    );
};
