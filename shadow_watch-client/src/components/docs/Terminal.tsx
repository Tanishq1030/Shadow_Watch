import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface TerminalProps {
    children: React.ReactNode;
}

export const Terminal = ({ children }: TerminalProps) => {
    const terminalRef = useRef<HTMLDivElement>(null);
    const [isInView, setIsInView] = useState(false);
    const [ripples, setRipples] = useState<{ x: number; y: number; id: number }[]>([]);

    useEffect(() => {
        if (!terminalRef.current) return;

        const element = terminalRef.current;

        const trigger = ScrollTrigger.create({
            trigger: element,
            start: 'top 80%',
            onEnter: () => {
                setIsInView(true);
                gsap.from(element, {
                    opacity: 0,
                    y: 10,
                    duration: 0.3,
                    ease: 'power1.out',
                });
            },
            once: true,
        });

        const onEnter = () => {
            gsap.to(element, {
                scale: 1.02,
                boxShadow: '0 0 30px rgba(139, 92, 246, 0.5)',
                duration: 0.3,
            });
        };

        const onLeave = () => {
            gsap.to(element, {
                scale: 1,
                boxShadow: 'none',
                duration: 0.3,
            });
        };

        element.addEventListener('mouseenter', onEnter);
        element.addEventListener('mouseleave', onLeave);

        return () => {
            trigger.kill();
            element.removeEventListener('mouseenter', onEnter);
            element.removeEventListener('mouseleave', onLeave);
        };
    }, []);

    const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = terminalRef.current?.getBoundingClientRect();
        if (!rect) return;
        const id = Date.now();
        setRipples((prev) => [...prev, { x: e.clientX - rect.left, y: e.clientY - rect.top, id }]);
        setTimeout(() => setRipples((prev) => prev.filter((r) => r.id !== id)), 600);
    };

    return (
        <div
            ref={terminalRef}
            onClick={handleClick}
            className="relative bg-black border border-zinc-800 rounded my-6 overflow-hidden cursor-pointer font-mono"
        >
            {ripples.map((r) => (
                <span
                    key={r.id}
                    className="absolute pointer-events-none rounded-full"
                    style={{
                        left: r.x,
                        top: r.y,
                        width: 0,
                        height: 0,
                        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.6) 0%, transparent 70%)',
                        animation: 'ripple-expand 0.6s ease-out',
                    }}
                />
            ))}

            {React.Children.map(children, (child) => {
                if (React.isValidElement(child)) {
                    return React.cloneElement(child, { isInView } as any);
                }
                return child;
            })}
        </div>
    );
};

export const TerminalHeader = ({ children, isInView }: { children: React.ReactNode; isInView?: boolean }) => {
    return (
        <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950 flex items-center gap-2 text-lg">
            <span className="text-violet-400 font-bold">$</span>
            <span className="text-cyan-400">{children}</span>
        </div>
    );
};

export const TerminalBody = ({
    children,
    isInView,
    mode = 'text',
}: {
    children: React.ReactNode;
    isInView?: boolean;
    mode?: 'code' | 'text';
}) => {
    // Mode "text" - render immediately, no typing
    if (mode === 'text') {
        return <div className="p-6 text-base leading-relaxed">{children}</div>;
    }

    // Mode "code" - render with typing (handled by parent providing CodeTyping component)
    return <div className="p-6 text-base leading-relaxed">{children}</div>;
};
