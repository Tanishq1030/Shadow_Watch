import FeatureCard from "./FeatureCard";
import ScrollReveal from "./ScrollReveal";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const features = [
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-ghost"><path d="M9 10h.01" /><path d="M15 10h.01" /><path d="M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z" /></svg>, // Ghost/Silent icon
    title: "Silent Tracking",
    description: "Our SDK operates entirely in the background, capturing user interactions with zero UI impact. It uses non-blocking asynchronous calls to ensure your application's performance remains silky smooth while gathering deep behavioral insights.",
    variant: "default" as const,
    color: "purple" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-fingerprint"><path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4" /><path d="M21 12a9 9 0 1 1-18 0" /><path d="M15.8 22a9.94 9.94 0 0 0 5.2-7.8" /><path d="M12 6a6 6 0 0 1 6 6c0 .76-.08 2.05-.23 3.5" /><path d="M4.2 14.8c.2-.9.5-2.2.9-3.3a9.94 9.94 0 0 1 5.2-7.9" /><path d="M9 16.5c.3-1.8.8-3.4 1.3-4.5" /><path d="M19.7 18.2a9.94 9.94 0 0 1-5.6 3.7" /></svg>, // Fingerprint
    title: "Behavioral Fingerprinting",
    description: "We generate a unique behavioral signature for every user by analyzing click patterns, navigation speed, and session timing. This allows for advanced fraud detection and spotting account sharing anomalies that traditional methods miss.",
    variant: "default" as const,
    color: "magenta" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-library"><path d="m16 6 4 14" /><path d="M12 6v14" /><path d="M8 8v12" /><path d="M4 4v16" /></svg>, // Library
    title: "Interest Library",
    description: "Shadow Watch automatically constructs a dynamic, ranked library of user interests. By synthesizing viewing history and trading actions, it creates a rich profile that evolves in real-time, perfect for personalization engines.",
    variant: "default" as const,
    color: "pink" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-shield-check"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-0.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" /><path d="m9 12 2 2 4-4" /></svg>, // Shield
    title: "Trust Score Engine",
    description: "Every session is evaluated in real-time to calculate a Trust Score from 0.0 to 1.0. This score aggregates multiple risk factors tailored to your security policies, enabling passive, high-confidence security checks without nagging users.",
    variant: "wide" as const,
    color: "rose" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-server"><rect width="20" height="8" x="2" y="2" rx="2" ry="2" /><rect width="20" height="8" x="2" y="14" rx="2" ry="2" /><line x1="6" x2="6.01" y1="6" y2="6" /><line x1="6" x2="6.01" y1="18" y2="18" /></svg>, // Server/Self-Hosted
    title: "100% Self-Hosted",
    description: "Maintain complete data sovereignty. Shadow Watch is designed to run entirely on your infrastructure, supporting PostgreSQL and Redis out of the box. No external dependencies, no data leakage, full compliance control.",
    variant: "default" as const,
    color: "orange" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-zap"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z" /></svg>, // Zap/Async
    title: "Async Performance",
    description: "Engineered for speed using Python's asyncio primitives. All tracking operations are 'fire-and-forget', ensuring a latency footprint of less than 5ms, so your API response times stay lightning fast.",
    variant: "default" as const,
    color: "yellow" as const,
  },
  {
    icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-code-2"><path d="m18 16 4-4-4-4" /><path d="m6 8-4 4 4 4" /><path d="m14.5 4-5 16" /></svg>, // Code
    title: "Type-Safe SDK",
    description: "Our Python SDK is fully typed and built with Pydantic models. This ensures you catch integration errors at compile time, not in production, providing a robust developer experience with full IDE support.",
    variant: "default" as const,
    color: "amber" as const,
  },
];

const FeaturesGrid = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    },
  };

  return (
    <section className="py-24 px-4">
      <div className="container mx-auto">
        {/* Section header */}
        <ScrollReveal className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Why Shadow Watch?
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Engineered for the AI era, combining human readability with machine efficiency.
          </p>
        </ScrollReveal>

        {/* Features grid */}
        <motion.div
          ref={ref}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={itemVariants}>
              <FeatureCard
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                variant={feature.variant}
                color={feature.color}
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturesGrid;
