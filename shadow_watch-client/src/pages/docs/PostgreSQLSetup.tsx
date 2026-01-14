import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const PostgreSQLSetup = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">PostgreSQL Setup</h1>
                    <p className="text-xl text-zinc-400">
                        Scale to millions of users with production-grade database
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            PostgreSQL is <span className="text-green-500">recommended for production</span>.
                            Handles millions of events/day. ACID compliance. Advanced indexing.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Installation</h2>

                    <CodeBlock
                        code={`# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@14

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql@14  # macOS`}
                        language="bash"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Create Database</h3>

                    <CodeBlock
                        code={`# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE shadowwatch;
CREATE USER shadowwatch_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE shadowwatch TO shadowwatch_user;

# Exit
\\q`}
                        language="sql"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Connection String</h2>

                    <CodeBlock
                        code={`# Local development
DATABASE_URL=postgresql+asyncpg://shadowwatch_user:secure_password_here@localhost:5432/shadowwatch

# Production (AWS RDS)
DATABASE_URL=postgresql+asyncpg://admin:password@shadowwatch.abc123.us-east-1.rds.amazonaws.com:5432/shadowwatch

# Production (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:password@db.abc123.supabase.co:5432/postgres`}
                        filename=".env"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Indexes for Performance</h2>

                    <p className="mb-4">Shadow Watch creates these indexes automatically:</p>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch show-indexes
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-2 font-mono text-xs text-zinc-400">
                                <div>user_activities: (user_id, created_at)</div>
                                <div>user_profiles: (user_id) PRIMARY KEY</div>
                                <div>interest_library: (user_id, entity_id) COMPOSITE</div>
                                <div>trust_events: (user_id, created_at)</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <h3 className="text-xl font-bold mt-8 mb-4">Manual Index Optimization (Optional)</h3>

                    <CodeBlock
                        code={`-- For heavy querying by entity_id
CREATE INDEX idx_activities_entity ON user_activities(entity_id);

-- For time-range queries
CREATE INDEX idx_activities_timestamp ON user_activities(created_at);

-- Partial index for high-value users
CREATE INDEX idx_high_value_users ON user_profiles(user_id) 
WHERE total_items > 1000;`}
                        language="sql"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Production Configuration</h2>

                    <CodeBlock
                        code={`# postgresql.conf optimizations
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB`}
                        filename="postgresql.conf"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Backup Strategy</h2>

                    <CodeBlock
                        code={`# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/shadowwatch"
DATE=$(date +%Y%m%d_%H%M%S)

# Dump database
pg_dump -U shadowwatch_user shadowwatch > "$BACKUP_DIR/shadowwatch_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/shadowwatch_$DATE.sql"

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/shadowwatch_$DATE.sql.gz" s3://my-backups/shadowwatch/`}
                        language="bash"
                        filename="backup.sh"
                    />

                    <p className="mt-4">Schedule with cron:</p>
                    <CodeBlock
                        code={`# Run daily at 2 AM
0 2 * * * /path/to/backup.sh`}
                        language="bash"
                        filename="crontab"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Monitoring</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> psql shadowwatch -c "SELECT ..."
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs">
                                <div className="text-zinc-500"># Check database size</div>
                                <div className="text-green-500">SELECT pg_size_pretty(pg_database_size('shadowwatch'));</div>
                                <div className="text-zinc-400 mt-2">→ 2.3 GB</div>

                                <div className="text-zinc-500 mt-4"># Active connections</div>
                                <div className="text-green-500">SELECT count(*) FROM pg_stat_activity;</div>
                                <div className="text-zinc-400 mt-2">→ 23</div>

                                <div className="text-zinc-500 mt-4"># Slow queries</div>
                                <div className="text-green-500">SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5;</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>
            </article>
        </div>
    );
};
