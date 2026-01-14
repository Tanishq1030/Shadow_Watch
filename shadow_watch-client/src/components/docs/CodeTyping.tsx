import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { highlightPython } from '../../lib/highlight';

interface CodeTypingProps {
    code: string;
    play: boolean;
    typingSpeedMs?: number;
    onComplete?: () => void;
}

// Split Shiki HTML into character-level spans while preserving colors
const splitIntoCharacterSpans = (shikiHTML: string): string => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(shikiHTML, 'text/html');
    const pre = doc.querySelector('pre');

    if (!pre) return shikiHTML;

    // Process each line
    const lines = pre.querySelectorAll('.line');
    lines.forEach((line) => {
        const newContent: Node[] = [];

        // Process each token span in the line
        line.childNodes.forEach((node) => {
            if (node.nodeType === Node.TEXT_NODE) {
                // Plain text - wrap each character
                const text = node.textContent || '';
                text.split('').forEach((char) => {
                    const span = document.createElement('span');
                    span.className = 'code-char';
                    span.textContent = char === ' ' ? '\u00A0' : char;
                    newContent.push(span);
                });
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const element = node as HTMLElement;
                const text = element.textContent || '';
                const color = element.style.color; // Shiki uses inline styles!

                // Split token into character spans, preserving color
                text.split('').forEach((char) => {
                    const span = document.createElement('span');
                    span.className = 'code-char';
                    if (color) {
                        span.style.color = color; // Preserve Shiki's color
                    }
                    span.textContent = char === ' ' ? '\u00A0' : char;
                    newContent.push(span);
                });
            }
        });

        // Replace line content
        line.innerHTML = '';
        newContent.forEach((node) => line.appendChild(node));
    });

    return pre.outerHTML;
};

export const CodeTyping = ({
    code,
    play,
    typingSpeedMs = 40,
    onComplete,
}: CodeTypingProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const cursorRef = useRef<HTMLSpanElement>(null);
    const timelineRef = useRef<gsap.core.Timeline | null>(null);
    const reducedMotion = useReducedMotion();
    const [processedHTML, setProcessedHTML] = useState<string>('');

    // Highlight code and split into character spans
    useEffect(() => {
        highlightPython(code).then((html) => {
            const charHTML = splitIntoCharacterSpans(html);
            setProcessedHTML(charHTML);
        });
    }, [code]);

    useEffect(() => {
        if (!play || reducedMotion || !processedHTML) return;
        if (!containerRef.current) return;

        // Get all character spans
        const chars = containerRef.current.querySelectorAll<HTMLSpanElement>('.code-char');
        const cursor = cursorRef.current;

        if (!cursor || chars.length === 0) return;

        const ctx = gsap.context(() => {
            // Hide all characters initially
            gsap.set(chars, { opacity: 0 });
            gsap.set(cursor, { opacity: 1 });

            const tl = gsap.timeline({
                onComplete: () => {
                    onComplete?.();
                    gsap.to(cursor, { opacity: 0, duration: 0.3, delay: 1 });
                },
            });

            timelineRef.current = tl;

            // Type each character
            chars.forEach((char, index) => {
                tl.to(char, {
                    opacity: 1,
                    duration: 0,
                }, typingSpeedMs * index / 1000)
                    .call(() => {
                        // Move cursor after this character
                        if (char.nextSibling && char.nextSibling === cursor) return;
                        char.parentElement?.insertBefore(cursor, char.nextSibling);
                    }, undefined, typingSpeedMs * index / 1000);
            });
        }, containerRef);

        return () => {
            ctx.revert();
            timelineRef.current = null;
        };
    }, [play, reducedMotion, typingSpeedMs, onComplete, processedHTML]);

    // Reduced motion - show immediately with colors
    if (reducedMotion && processedHTML) {
        return (
            <div
                ref={containerRef}
                className="shiki-terminal"
                dangerouslySetInnerHTML={{ __html: processedHTML }}
            />
        );
    }

    // Still loading
    if (!processedHTML) {
        return <div className="p-6">Loading...</div>;
    }

    return (
        <div ref={containerRef} className="relative shiki-terminal">
            <span ref={cursorRef} className="typing-cursor inline-block" aria-hidden="true">
                ▋
            </span>
            <div dangerouslySetInnerHTML={{ __html: processedHTML }} />
        </div>
    );
};
