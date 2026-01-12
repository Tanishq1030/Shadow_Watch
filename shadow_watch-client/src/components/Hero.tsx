import { ArrowRight, Copy } from "lucide-react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

const Hero = () => {
  // Fetch server version dynamically
  const { data: serverInfo } = useQuery({
    queryKey: ['server-version'],
    queryFn: async () => {
      const res = await fetch('https://shadow-watch-three.vercel.app/');
      return res.json();
    },
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });

  const version = serverInfo?.version || '1.0.4'; // Fallback

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background to-secondary/20" />

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, hsl(var(--foreground)) 1px, transparent 0)`,
          backgroundSize: '40px 40px',
        }}
      />

      <div className="container relative z-10 mx-auto px-4 text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex flex-col items-center gap-4 mb-8"
        >
          <div className="inline-flex items-center gap-2 rounded-full bg-[#1A2E22] border border-[#2D4A38] px-6 py-1">
            <span className="text-xs font-medium text-[#10B981] tracking-wide">
              PRODUCTION READY V{version}
            </span>
          </div>
          <span className="text-[10px] tracking-[0.2em] text-muted-foreground font-bold uppercase">
            Supported in: Python • FastAPI • Django • Flask
          </span>
        </motion.div>

        {/* Main headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-6xl md:text-8xl lg:text-9xl font-black tracking-tighter mb-8 leading-[0.9]"
        >
          <span className="block text-transparent bg-clip-text bg-gradient-to-b from-neutral-800 via-neutral-600 to-neutral-400 dark:from-white/90 dark:via-white/50 dark:to-white/10" style={{ textShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>BEHAVIORAL</span>
          <span className="block text-transparent bg-clip-text bg-gradient-to-b from-neutral-800 via-neutral-600 to-neutral-400 dark:from-white/90 dark:via-white/50 dark:to-white/10" style={{ textShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>INTELLIGENCE</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="max-w-2xl mx-auto text-lg md:text-xl text-muted-foreground mb-10"
        >
          Track user interests silently. Build behavioral profiles automatically.
          Prevent account takeover with zero friction.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="flex flex-wrap items-center justify-center gap-6 mb-24"
        >
          <Button
            size="lg"
            className="gap-3 px-10 h-16 text-xl font-bold bg-zinc-900 text-zinc-100 hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white transition-all shadow-[0_0_20px_rgba(0,0,0,0.1)] dark:shadow-[0_0_20px_rgba(255,255,255,0.2)]"
            onClick={() => window.open("https://github.com/Tanishq1030/Shadow_Watch", "_blank")}
          >
            GitHub
            <ArrowRight className="h-6 w-6" />
          </Button>
          <Button variant="outline" size="lg" className="px-10 h-16 text-xl font-bold border-zinc-200 bg-white/50 text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-black/50 dark:text-zinc-100 dark:hover:bg-zinc-900 transition-all">
            Case Study
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="px-10 h-16 text-xl font-bold border-zinc-200 bg-white/50 text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-black/50 dark:text-zinc-100 dark:hover:bg-zinc-900 transition-all"
            onClick={() => window.open("https://discord.com/channels/1460051701389070504/1460051702110748990", "_blank")}
          >
            Join Discord
          </Button>
        </motion.div>

        {/* Install command */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="inline-flex items-center gap-5 rounded-2xl bg-[#0d1117] border border-white/10 px-8 py-5 shadow-2xl"
        >
          <span className="text-zinc-500 text-xl font-mono select-none">$</span>
          <code className="text-xl font-mono">
            <span className="text-blue-400">pip</span>{" "}
            <span className="text-zinc-100">install</span>{" "}
            <span className="text-yellow-400">shadowwatch</span>
          </code>
          <button
            className="p-2.5 rounded-lg hover:bg-white/10 transition-colors ml-2 group"
            onClick={() => navigator.clipboard.writeText("pip install shadowwatch")}
          >
            <Copy className="h-5 w-5 text-zinc-500 group-hover:text-zinc-300 transition-colors" />
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
