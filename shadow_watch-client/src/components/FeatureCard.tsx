import { LucideIcon } from "lucide-react";
import { useRef } from "react";
import React from "react";

interface FeatureCardProps {
  icon: React.ReactNode | LucideIcon;
  title: string;
  description: string;
  variant?: "default" | "wide";
  color?: "purple" | "magenta" | "pink" | "rose" | "orange" | "yellow" | "amber" | "red";
}

const colorClasses = {
  purple: {
    bg: "bg-purple-500/10",
    border: "border-purple-500/30 group-hover:border-purple-500/50",
    icon: "text-purple-400 group-hover:text-purple-300",
    gradient: "hsl(271 81% 56%)",
  },
  magenta: {
    bg: "bg-fuchsia-500/10",
    border: "border-fuchsia-500/30 group-hover:border-fuchsia-500/50",
    icon: "text-fuchsia-400 group-hover:text-fuchsia-300",
    gradient: "hsl(300 76% 72%)",
  },
  pink: {
    bg: "bg-pink-500/10",
    border: "border-pink-500/30 group-hover:border-pink-500/50",
    icon: "text-pink-400 group-hover:text-pink-300",
    gradient: "hsl(330 80% 60%)",
  },
  rose: {
    bg: "bg-rose-500/10",
    border: "border-rose-500/30 group-hover:border-rose-500/50",
    icon: "text-rose-400 group-hover:text-rose-300",
    gradient: "hsl(350 89% 60%)",
  },
  orange: {
    bg: "bg-orange-500/10",
    border: "border-orange-500/30 group-hover:border-orange-500/50",
    icon: "text-orange-400 group-hover:text-orange-300",
    gradient: "hsl(25 95% 53%)",
  },
  yellow: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30 group-hover:border-yellow-500/50",
    icon: "text-yellow-400 group-hover:text-yellow-300",
    gradient: "hsl(48 96% 53%)",
  },
  amber: {
    bg: "bg-amber-500/10",
    border: "border-amber-500/30 group-hover:border-amber-500/50",
    icon: "text-amber-400 group-hover:text-amber-300",
    gradient: "hsl(38 92% 50%)",
  },
  red: {
    bg: "bg-red-500/10",
    border: "border-red-500/30 group-hover:border-red-500/50",
    icon: "text-red-400 group-hover:text-red-300",
    gradient: "hsl(0 84% 60%)",
  },
};

const FeatureCard = ({ icon: IconOrNode, title, description, variant = "default", color = "purple" }: FeatureCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const colors = colorClasses[color];

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    cardRef.current.style.setProperty('--mouse-x', `${x}%`);
    cardRef.current.style.setProperty('--mouse-y', `${y}%`);
  };

  const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    cardRef.current.style.setProperty('--card-gradient', colors.gradient);
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      className={`
        group relative rounded-xl p-10 card-glow-unique bg-gradient-animated cursor-pointer flex flex-col min-h-[380px] transition-all duration-300 hover:scale-[1.02]
        ${variant === "wide" ? "md:col-span-2" : ""}
      `}
    >
      {/* Icon container */}
      <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl ${colors.bg} backdrop-blur-sm border ${colors.border} transition-colors`}>
        {React.isValidElement(IconOrNode) ? (
          <div className={`h-5 w-5 ${colors.icon} transition-colors child-svg-current`}>
            {IconOrNode}
          </div>
        ) : (
          // Cast to LucideIcon for rendering
          (() => {
            const Icon = IconOrNode as LucideIcon;
            return <Icon className={`h-5 w-5 ${colors.icon} transition-colors`} />;
          })()
        )}
      </div>

      {/* Content */}
      {/* Content */}
      <h3 className="text-2xl font-bold mb-3 text-foreground group-hover:text-foreground transition-colors">
        {title}
      </h3>
      <p className="text-base text-muted-foreground leading-relaxed">
        {description}
      </p>

      {/* Learn more link */}

    </div>
  );
};

export default FeatureCard;
