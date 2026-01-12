import { Building2, ShoppingCart, DollarSign, CreditCard, Users, MessageCircle } from "lucide-react";
import ScrollReveal from "./ScrollReveal";

const logos = [
  { name: "Stripe", icon: CreditCard },
  { name: "PayPal", icon: DollarSign },
  { name: "Square", icon: Building2 },
  { name: "Shopify", icon: ShoppingCart },
  { name: "Meta", icon: Users },
  { name: "Discord", icon: MessageCircle },
];

const LogoScroll = () => {
  return (
    <section className="relative py-16 border-y border-border/50 overflow-hidden bg-secondary">
      <ScrollReveal>
        <div className="text-center mb-10">
          <p className="text-xl font-medium text-muted-foreground">
            Shadow Watch can be used in any company from any field
          </p>
        </div>
      </ScrollReveal>

      {/* Infinite scroll container */}
      <div className="relative">
        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-secondary to-transparent z-10" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-secondary to-transparent z-10" />

        {/* Scrolling logos - duplicate sets for seamless loop */}
        <div className="flex animate-scroll w-max">
          {/* Create 12 sets of logos (Optimized Loop) */}
          {Array.from({ length: 12 }).map((_, setIndex) => (
            logos.map((logo, index) => {
              const Icon = logo.icon;
              return (
                <div
                  key={`logo-${setIndex}-${index}`}
                  className="flex items-center gap-3 mx-4 px-6 py-3 rounded-full bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-md border border-white/10 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)] shrink-0 group hover:bg-white/10 transition-all duration-300"
                >
                  <Icon className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                  <span className="text-base font-medium text-muted-foreground group-hover:text-foreground transition-colors whitespace-nowrap">
                    {logo.name}
                  </span>
                </div>
              );
            })
          ))}
        </div>
      </div>
    </section>
  );
};

export default LogoScroll;
