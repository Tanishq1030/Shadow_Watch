import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const ParallaxBackground = () => {
    const bgRef = useRef<HTMLDivElement>(null);
    const layer1Ref = useRef<HTMLDivElement>(null);
    const layer2Ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!bgRef.current || !layer1Ref.current || !layer2Ref.current) return;

        // Layer 1 - Slow parallax
        gsap.to(layer1Ref.current, {
            y: 100,
            ease: 'none',
            scrollTrigger: {
                trigger: bgRef.current,
                start: 'top top',
                end: 'bottom top',
                scrub: 1.5,
            },
        });

        // Layer 2 - Medium parallax
        gsap.to(layer2Ref.current, {
            y: 200,
            ease: 'none',
            scrollTrigger: {
                trigger: bgRef.current,
                start: 'top top',
                end: 'bottom top',
                scrub: 1,
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
        };
    }, []);

    return (
        <div ref={bgRef} className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
            {/* Layer 1 - Slow moving grid */}
            <div
                ref={layer1Ref}
                className="absolute inset-0 opacity-[0.02]"
                style={{
                    backgroundImage: `radial-gradient(circle at 1px 1px, rgba(139, 92, 246, 0.3) 1px, transparent 0)`,
                    backgroundSize: '60px 60px',
                }}
            />

            {/* Layer 2 - Faster moving gradient */}
            <div
                ref={layer2Ref}
                className="absolute inset-0 opacity-20"
                style={{
                    background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.15) 0%, transparent 50%)',
                }}
            />
        </div>
    );
};
