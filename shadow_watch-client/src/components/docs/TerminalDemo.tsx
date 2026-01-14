import { useState, useEffect, useRef } from 'react';
import { Terminal, TerminalHeader, TerminalBody } from './Terminal';
import { CodeTyping } from './CodeTyping';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface TerminalDemoProps {
    title: string;
    mode: 'code' | 'text';
    language?: 'python' | 'bash' | 'javascript';
    code?: string;
    children?: React.ReactNode;
    autoplay?: boolean;
}

export const TerminalDemo = ({
    title,
    mode,
    language = 'bash',
    code,
    children,
    autoplay = true,
}: TerminalDemoProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isInView, setIsInView] = useState(false);

    useEffect(() => {
        if (!containerRef.current || !autoplay) return;

        const trigger = ScrollTrigger.create({
            trigger: containerRef.current,
            start: 'top 70%',
            onEnter: () => setIsInView(true),
            once: true,
        });

        return () => trigger.kill();
    }, [autoplay]);

    return (
        <div ref={containerRef}>
            <Terminal>
                <TerminalHeader>{title}</TerminalHeader>
                <TerminalBody mode={mode}>
                    {mode === 'code' && code ? (
                        <CodeTyping code={code} play={isInView && autoplay} typingSpeedMs={40} />
                    ) : (
                        children
                    )}
                </TerminalBody>
            </Terminal>
        </div>
    );
};
