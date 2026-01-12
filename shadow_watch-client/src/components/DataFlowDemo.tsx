import { useState } from "react";
import { BarChart3, RefreshCcw, Sparkles, Copy, Check } from "lucide-react";
import ScrollReveal from "./ScrollReveal";
import { motion } from "framer-motion";
import { useRef } from "react";

const tabs = [
  { id: "analytics", label: "Analytics", icon: BarChart3 },
  { id: "transform", label: "Transform", icon: RefreshCcw },
  { id: "reasoning", label: "Reasoning", icon: Sparkles },
];

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: "cyan" | "purple" | "green";
}

const GlassCard = ({ children, className = "", glowColor = "cyan" }: GlassCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    cardRef.current.style.setProperty('--mouse-x', `${x}%`);
    cardRef.current.style.setProperty('--mouse-y', `${y}%`);
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      className={`group relative rounded-xl card-glow bg-gradient-animated ${className}`}
    >
      {children}
    </div>
  );
};

const DataFlowDemo = () => {
  const [activeTab, setActiveTab] = useState("analytics");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-24 px-4 bg-secondary/20">
      <div className="container mx-auto">
        {/* Section header */}
        <ScrollReveal className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Live Behavioral Tracking
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Shadow Watch silently tracks user behavior and builds trust profiles in real-time.
          </p>
        </ScrollReveal>

        {/* Tabs */}
        <ScrollReveal delay={0.1} className="flex justify-center mb-12">
          <div className="inline-flex items-center gap-1 p-1 rounded-xl bg-secondary border border-border">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                    ${activeTab === tab.id
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </ScrollReveal>

        {/* Data flow visualization */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          {/* Input Card */}
          <ScrollReveal delay={0.2} direction="left">
            <GlassCard className="p-5 h-full bg-gradient-to-br from-purple-950/20 to-transparent">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-8 w-8 rounded-lg bg-purple-500/10 backdrop-blur-sm flex items-center justify-center border border-purple-500/30 group-hover:border-purple-500/50 transition-colors">
                  <BarChart3 className="h-4 w-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
                </div>
                <div>
                  <h4 className="font-semibold text-sm">INPUT DATA</h4>
                  <p className="text-xs text-muted-foreground">Activity Tracker</p>
                </div>
              </div>

              <div className="mb-3">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Context</span>
              </div>

              <div className="code-block rounded-lg p-3 text-xs font-mono overflow-x-auto backdrop-blur-sm">
                <div className="text-muted-foreground">users:@(5):email,id,last_login,tier</div>
                <div>alice@ex.com,1,2024-12-08,premium</div>
                <div>bob@site.co,2,2024-11-15,pro</div>
                <div>carol@demo.org,3,2024-12-01,free</div>
                <div>dave@net.io,4,2024-10-20,premium</div>
                <div>eve@corp.ai,5,2024-12-09,pro</div>
              </div>

              <div className="mt-4 rounded-lg bg-primary/10 border border-primary/20 p-3 backdrop-blur-sm">
                <div className="flex items-center gap-2 text-primary text-xs mb-1">
                  <span>→</span>
                  <span className="uppercase tracking-wider">Query</span>
                </div>
                <p className="text-sm text-foreground">
                  Return keys & tiers for users who logged in after Dec 1st.
                </p>
              </div>
            </GlassCard>
          </ScrollReveal>

          {/* Output Card - with connector dots */}
          <ScrollReveal delay={0.3} className="relative">
            {/* Connector dots - left */}
            <div className="hidden lg:block absolute left-0 top-1/2 -translate-x-full -translate-y-1/2">
              <div className="flex items-center gap-1">
                <div className="w-8 h-0.5 bg-gradient-to-r from-transparent to-border" />
                <motion.div
                  animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="h-2 w-2 rounded-full bg-primary"
                />
              </div>
            </div>

            {/* Connector dots - right */}
            <div className="hidden lg:block absolute right-0 top-1/2 translate-x-full -translate-y-1/2">
              <div className="flex items-center gap-1">
                <motion.div
                  animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                  className="h-2 w-2 rounded-full bg-primary"
                />
                <div className="w-8 h-0.5 bg-gradient-to-r from-border to-transparent" />
              </div>
            </div>

            <GlassCard className="p-5 h-full bg-gradient-to-br from-orange-950/20 to-transparent">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-orange-500/10 backdrop-blur-sm flex items-center justify-center border border-orange-500/30 group-hover:border-orange-500/50 transition-colors">
                    <span className="text-orange-400 font-mono text-sm">{">"}_</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm">OUTPUT</h4>
                    <p className="text-xs text-muted-foreground">LLM Stream</p>
                  </div>
                </div>
                <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full backdrop-blur-sm">
                  Complete
                </span>
              </div>

              <div className="code-block rounded-lg p-3 relative backdrop-blur-sm">
                <button
                  onClick={handleCopy}
                  className="absolute top-2 right-2 p-1.5 rounded hover:bg-secondary transition-colors"
                >
                  {copied ? (
                    <Check className="h-3.5 w-3.5 text-primary" />
                  ) : (
                    <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                </button>
                <div className="font-mono text-xs">
                  <div className="text-muted-foreground">users:@(3):id,tier</div>
                  <div>1,premium</div>
                  <div>3,free</div>
                  <div>5,pro</div>
                </div>
              </div>
            </GlassCard>
          </ScrollReveal>

          {/* Decoder Card */}
          <ScrollReveal delay={0.5} direction="right">
            <GlassCard className="p-5 bg-gradient-to-br from-pink-950/20 to-transparent">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-8 w-8 rounded-lg bg-pink-500/10 backdrop-blur-sm flex items-center justify-center border border-pink-500/30 group-hover:border-pink-500/50 transition-colors">
                  <span className="text-pink-400 group-hover:text-pink-300 transition-colors font-mono text-sm">{"</>"}</span>
                </div>
                <div>
                  <h4 className="font-semibold text-sm">DECODER</h4>
                  <p className="text-xs text-muted-foreground">JSON Output</p>
                </div>
              </div>

              <div className="code-block rounded-lg p-3 font-mono text-xs backdrop-blur-sm">
                <div className="text-muted-foreground">{"{"}</div>
                <div className="pl-4">"users": [</div>
                <div className="pl-8">{"{ \"id\": 1, \"tier\": \"premium\" },"}</div>
                <div className="pl-8">{"{ \"id\": 3, \"tier\": \"free\" },"}</div>
                <div className="pl-8">{"{ \"id\": 5, \"tier\": \"pro\" }"}</div>
                <div className="pl-4">]</div>
                <div className="text-muted-foreground">{"}"}</div>
              </div>
            </GlassCard>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
};

export default DataFlowDemo;
