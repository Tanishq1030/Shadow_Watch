import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const MySQLConfiguration = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">MySQL Configuration</h1>
                    <p className="text-xl text-zinc-400">
                        Migrating from legacy systems to Shadow Watch
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            Already using MySQL? Shadow Watch supports it. Perfect for
                            <span className="text-green-500"> enterprises with existing MySQL infrastructure</span>.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Installation</h2>

                    <CodeBlock
                        code={`# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# macOS
brew install mysql

# Start MySQL
sudo systemctl start mysql  # Linux
brew services start mysql  # macOS`}
                        language="bash"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Create Database</h3>

                    <CodeBlock
                        code={`mysql -u root -p

CREATE DATABASE shadowwatch CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shadowwatch'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shadowwatch.* TO 'shadowwatch'@'localhost';
FLUSH PRIVILEGES;
EXIT;`}
                        language="sql"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Connection String</h2>

                    <CodeBlock
                        code={`# Install MySQL async driver
pip install aiomysql

# Connection string
DATABASE_URL=mysql+aiomysql://shadowwatch:secure_password@localhost:3306/shadowwatch

# Production (AWS RDS)
DATABASE_URL=mysql+aiomysql://admin:password@shadowwatch.abc123.us-east-1.rds.amazonaws.com:3306/shadowwatch`}
                        filename=".env"
                    />

                    <Terminal>
                        <TerminalBody mode="text">
                            <p className="text-sm text-yellow-500">
                                ⚠ Note: Use <code className="text-green-500">aiomysql</code> driver (async), not pymysql (sync)
                            </p>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Configuration (my.cnf)</h2>

                    <CodeBlock
                        code={`[mysqld]
# Character Set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Performance
max_connections = 200
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Query Cache (MySQL 5.7 only)
query_cache_type = 1
query_cache_size = 64M

# Slow Query Log
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 1`}
                        filename="/etc/mysql/my.cnf"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Monitoring</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> mysql -e "SHOW STATUS"
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-xs space-y-1">
                                <div className="text-zinc-400">Uptime: 432,000 seconds</div>
                                <div className="text-zinc-400">Queries: 12,847,234</div>
                                <div className="text-zinc-400">Slow_queries: 142</div>
                                <div className="text-green-500">Threads_connected: 18</div>
                                <div className="text-zinc-400">Bytes_received: 2.1 GB</div>
                                <div className="text-zinc-400">Bytes_sent: 5.7 GB</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">PostgreSQL vs MySQL</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch compare-databases
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="grid md:grid-cols-2 gap-8 font-mono text-xs">
                                <div>
                                    <div className="text-green-500 font-bold mb-2">PostgreSQL</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>✓ Better JSON support</div>
                                        <div>✓ Advanced indexing (GIN, GiST)</div>
                                        <div>✓ Stronger ACID compliance</div>
                                        <div>✓ Better for complex queries</div>
                                        <div className="text-green-500 mt-2">→ Recommended</div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-yellow-500 font-bold mb-2">MySQL</div>
                                    <div className="space-y-1 text-zinc-400">
                                        <div>✓ Simpler setup</div>
                                        <div>✓ Wide  enterprise adoption</div>
                                        <div>✓ Great for read-heavy</div>
                                        <div>✓ Easier replication</div>
                                        <div className="text-yellow-500 mt-2">→ Also good!</div>
                                    </div>
                                </div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>
            </article>
        </div>
    );
};
