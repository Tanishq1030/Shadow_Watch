import FeatureCard from "./FeatureCard";
import ScrollReveal from "./ScrollReveal";

const CodeDemo = () => {
    return (
        <section className="py-24 px-4">
            <div className="container mx-auto max-w-7xl">
                <ScrollReveal className="mb-16 text-center lg:text-left">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Seamless Integration
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto lg:mx-0">
                        Drop-in with 3 lines of code. Shadow Watch updates your interest library in the background.
                    </p>
                </ScrollReveal>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Step 1: Input Code */}
                    <ScrollReveal delay={0.1} className="lg:col-span-1">
                        <div className="rounded-2xl border border-border bg-card overflow-hidden h-full flex flex-col shadow-xl min-h-[420px]">
                            <div className="px-8 py-5 border-b border-border/50 bg-muted/20">
                                <h3 className="font-bold text-base uppercase tracking-wider text-muted-foreground">1. Minimal Setup</h3>
                            </div>
                            <div className="p-8 bg-[#0d1117] flex-1 font-mono text-base overflow-x-auto leading-relaxed">
                                <code className="text-blue-400">from</code> <code className="text-foreground">shadow_watch</code> <code className="text-blue-400">import</code> <code className="text-yellow-300">ShadowWatch</code>
                                <br /><br />
                                <code className="text-gray-500"># Initialize once</code>
                                <br />
                                <code className="text-foreground">sw</code> <code className="text-blue-400">=</code> <code className="text-yellow-300">ShadowWatch</code><code className="text-foreground">(</code><code className="text-orange-300">db_url</code><code className="text-blue-400">=</code><code className="text-foreground">...</code><code className="text-foreground">)</code>
                                <br /><br />
                                <code className="text-purple-400">await</code> <code className="text-foreground">sw</code><code className="text-blue-400">.track</code><code className="text-foreground">(</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-orange-300">user_id</code><code className="text-blue-400">=</code><code className="text-green-400">"usr_123"</code><code className="text-foreground">,</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-orange-300">event</code><code className="text-blue-400">=</code><code className="text-green-400">"view_ticker"</code><code className="text-foreground">,</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-orange-300">metadata</code><code className="text-blue-400">=</code><code className="text-foreground">{"{"}</code><code className="text-green-400">"s"</code><code className="text-foreground">:</code> <code className="text-green-400">"AAPL"</code><code className="text-foreground">{"}"}</code>
                                <br />
                                <code className="text-foreground">)</code>
                            </div>
                        </div>
                    </ScrollReveal>

                    {/* Step 2: Processing (Visual) */}
                    <ScrollReveal delay={0.2} className="lg:col-span-1">
                        <div className="rounded-2xl border border-border bg-card overflow-hidden h-full flex flex-col shadow-xl min-h-[420px]">
                            <div className="px-8 py-5 border-b border-border/50 bg-muted/20">
                                <h3 className="font-bold text-base uppercase tracking-wider text-muted-foreground">2. Passive Analysis</h3>
                            </div>
                            <div className="p-8 flex-1 flex flex-col items-center justify-center gap-8 relative bg-gradient-to-b from-background to-muted/20">
                                <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:24px_24px]" />

                                <div className="relative z-10 p-6 rounded-full bg-primary/10 border border-primary/20 animate-pulse scale-125">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M2 12h20" /><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6" /><path d="M12 2a5 5 0 0 1 5 5v5H7V7a5 5 0 0 1 5-5z" /><path d="M12 22v-5" /></svg>
                                </div>
                                <div className="text-center z-10">
                                    <h4 className="font-bold text-xl text-foreground mb-3">Async Processing</h4>
                                    <p className="text-base text-muted-foreground w-64 mx-auto leading-relaxed">
                                        Events are processed in background workers. Zero latency impact on your API.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </ScrollReveal>

                    {/* Step 3: Library Output */}
                    <ScrollReveal delay={0.3} className="lg:col-span-1">
                        <div className="rounded-2xl border border-border bg-card overflow-hidden h-full flex flex-col shadow-xl min-h-[420px]">
                            <div className="px-8 py-5 border-b border-border/50 bg-muted/20">
                                <h3 className="font-bold text-base uppercase tracking-wider text-muted-foreground">3. Interest Library</h3>
                            </div>
                            <div className="p-8 bg-[#0d1117] flex-1 font-mono text-base overflow-x-auto leading-relaxed">
                                <code className="text-gray-500">## Generated Profile</code>
                                <br /><br />
                                <code className="text-foreground">{"{"}</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-green-400">"trust_score"</code><code className="text-foreground">:</code> <code className="text-blue-400">0.98</code><code className="text-foreground">,</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-green-400">"top_interests"</code><code className="text-foreground">: [</code>
                                <br />
                                &nbsp;&nbsp;&nbsp;&nbsp;<code className="text-green-400">"Technology"</code><code className="text-foreground">,</code>
                                <br />
                                &nbsp;&nbsp;&nbsp;&nbsp;<code className="text-green-400">"AAPL"</code><code className="text-foreground">,</code>
                                <br />
                                &nbsp;&nbsp;&nbsp;&nbsp;<code className="text-green-400">"Semiconductors"</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-foreground">],</code>
                                <br />
                                &nbsp;&nbsp;<code className="text-green-400">"last_active"</code><code className="text-foreground">:</code> <code className="text-green-400">"2m ago"</code>
                                <br />
                                <code className="text-foreground">{"}"}</code>
                            </div>
                        </div>
                    </ScrollReveal>
                </div>
            </div>
        </section>
    );
};

export default CodeDemo;
