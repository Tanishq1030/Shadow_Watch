import { Crown } from "lucide-react";
import ScrollReveal from "./ScrollReveal";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const benchmarks = [
  {
    name: "Shadow Watch",
    score: 1450.8,
    integration: "Rapid",
    friction: "Zero",
    privacy: "Self-Hosted",
    cost: "Free (MIT)",
    latency: "Async",
    isTop: true
  },
  {
    name: "Passkeys",
    score: 1100.5,
    integration: "Complex",
    friction: "Low",
    privacy: "Device-Locked",
    cost: "Dev Cost",
    latency: "Fast",
    isTop: false
  },
  {
    name: "Auth0 / Clerk",
    score: 890.2,
    integration: "High Effort",
    friction: "Medium",
    privacy: "3rd Party",
    cost: "$$$ / User",
    latency: "Redirect",
    isTop: false
  },
  {
    name: "Authenticator App",
    score: 720.4,
    integration: "Moderate",
    friction: "High",
    privacy: "Device-Only",
    cost: "Free",
    latency: "Manual",
    isTop: false
  },
  {
    name: "Legacy Password",
    score: 400.1,
    integration: "Native",
    friction: "Critical",
    privacy: "Varies",
    cost: "Free",
    latency: "Manual",
    isTop: false
  },
];

const riskCoverage = [
  { name: "Shadow Watch", coverage: "99%", type: "Continuous Behavioral", width: "99%" },
  { name: "Standard 2FA", coverage: "45%", type: "Login-only Check", width: "45%" },
  { name: "Passwords", coverage: "15%", type: "Static Credential", width: "15%" },
];

const BenchmarkSection = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <section className="py-24 px-4 bg-background/50">
      <div className="w-full max-w-[1420px] mx-auto px-4">
        {/* Section header */}
        <ScrollReveal className="mb-16 text-center lg:text-left">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
            Shadow Watch vs Traditional Auth
          </h2>
          <p className="text-muted-foreground text-xl max-w-2xl mx-auto lg:mx-0">
            Passive intelligence provides better security with zero user friction.
          </p>
        </ScrollReveal>

        {/* Benchmark table */}
        <ScrollReveal delay={0.1}>
          <div ref={ref} className="rounded-2xl border border-border bg-card p-10 mb-16 shadow-2xl overflow-hidden">
            {/* Table Headers - Grid Layout */}
            <div className="hidden lg:grid grid-cols-12 gap-10 border-b border-border/50 pb-6 mb-6 px-6 text-sm font-bold text-muted-foreground uppercase tracking-widest">
              <div className="col-span-2 pl-2">Method</div>
              <div className="col-span-2">Score</div>
              <div className="col-span-2 text-center">Integration</div>
              <div className="col-span-2 text-center">Privacy</div>
              <div className="col-span-1 text-center">Cost</div>
              <div className="col-span-2 text-left pl-4">Latency</div>
              <div className="col-span-1 text-right pr-2">Friction</div>
            </div>

            <div className="space-y-3">
              {benchmarks.map((item, index) => (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className={`grid grid-cols-1 md:grid-cols-12 gap-10 items-center py-8 px-6 rounded-xl transition-all ${item.isTop
                    ? "bg-primary/5 border border-primary/20 shadow-sm"
                    : "hover:bg-muted/30 border border-transparent"
                    }`}
                >
                  {/* Name */}
                  <div className="col-span-2 font-semibold text-lg flex items-center gap-2">
                    <span className={item.isTop ? "text-primary" : "text-foreground"}>
                      {item.name}
                    </span>
                  </div>

                  {/* Score Bar */}
                  <div className="col-span-2 flex items-center gap-1.5">
                    {Array.from({ length: 12 }).map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ scaleY: 0 }}
                        animate={isInView ? { scaleY: 1 } : {}}
                        transition={{ duration: 0.3, delay: index * 0.1 + i * 0.02 }}
                        className={`h-10 w-2 rounded-[2px] origin-bottom ${i < Math.floor((item.score / 1500) * 12)
                          ? item.isTop ? "bg-primary" : "bg-muted-foreground/30"
                          : "bg-muted/20"
                          }`}
                      />
                    ))}
                    <span className={`ml-3 text-lg font-bold ${item.isTop ? "text-primary" : "text-muted-foreground"}`}>
                      {Math.round(item.score / 10)}
                    </span>
                  </div>

                  {/* Integration */}
                  <div className="col-span-2 text-center text-base font-medium text-muted-foreground/90">
                    <span className="lg:hidden text-xs uppercase text-muted-foreground mr-2">Integration:</span>
                    {item.integration}
                  </div>

                  {/* Privacy */}
                  <div className="col-span-2 text-center text-base font-medium text-muted-foreground/90">
                    <span className="lg:hidden text-xs uppercase text-muted-foreground mr-2">Privacy:</span>
                    {item.privacy}
                  </div>

                  {/* Cost */}
                  <div className="col-span-1 text-center text-base font-medium">
                    <span className="lg:hidden text-xs uppercase text-muted-foreground mr-2">Cost:</span>
                    <span className={item.cost.includes("Free") ? "text-green-500" : item.cost.includes("$") ? "text-red-400" : "text-muted-foreground"}>
                      {item.cost}
                    </span>
                  </div>

                  {/* Latency */}
                  <div className="col-span-2 text-left pl-4 text-base font-medium text-muted-foreground/90">
                    <span className="lg:hidden text-xs uppercase text-muted-foreground mr-2">Latency:</span>
                    {item.latency}
                  </div>

                  {/* Friction */}
                  <div className="col-span-1 lg:text-right text-base">
                    <span className="lg:hidden text-xs uppercase text-muted-foreground mr-2">Friction:</span>
                    <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${item.friction === "Zero"
                      ? "bg-green-500/15 text-green-500"
                      : item.friction === "Critical"
                        ? "bg-red-500/15 text-red-500"
                        : item.friction === "High"
                          ? "bg-orange-500/15 text-orange-500"
                          : "bg-blue-500/10 text-blue-500"
                      }`}>
                      {item.friction}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 pt-6 border-t border-border/50 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-3 bg-muted/20 rounded-lg">
                <div className="text-2xl font-bold text-foreground">50+</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Events Tracked</div>
              </div>
              <div className="p-3 bg-muted/20 rounded-lg">
                <div className="text-2xl font-bold text-foreground">Zero</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Latency Impact</div>
              </div>
              <div className="p-3 bg-muted/20 rounded-lg">
                <div className="text-2xl font-bold text-foreground">100%</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Control</div>
              </div>
              <div className="p-3 bg-muted/20 rounded-lg">
                <div className="text-2xl font-bold text-foreground">MIT</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Open Source</div>
              </div>
            </div>
          </div>
        </ScrollReveal>

        {/* Risk Coverage comparison */}
        <ScrollReveal delay={0.3}>
          <div className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-6">
              Risk Detection Coverage
            </h3>

            <div className="space-y-4">
              {riskCoverage.map((item, index) => (
                <div key={item.name} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium">{item.name}</div>
                  <div className="flex-1 h-6 bg-zinc-200 dark:bg-zinc-800 rounded-sm overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: item.width }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8, delay: index * 0.15, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-primary/60 to-muted-foreground/40 rounded-sm"
                    />
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    {item.coverage && (
                      <span className="text-primary font-medium hidden md:block">{item.coverage}</span>
                    )}
                    <span className="text-muted-foreground w-40 text-right">{item.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default BenchmarkSection;
