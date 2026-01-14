import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { prefersReducedMotion } from '@/animations/gsap-config';

interface UseTypingAnimationOptions {
    text: string;
    speed?: number;
    startDelay?: number;
    enabled?: boolean;
}

export const useTypingAnimation = (options: UseTypingAnimationOptions) => {
    const elementRef = useRef<HTMLSpanElement>(null);
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        if (!elementRef.current || prefersReducedMotion() || !options.enabled) {
            if (elementRef.current) {
                elementRef.current.textContent = options.text;
            }
            setIsComplete(true);
            return;
        }

        const element = elementRef.current;
        const chars = options.text.split('');

        // Clear and create character spans
        element.textContent = '';
        chars.forEach((char) => {
            const span = document.createElement('span');
            span.textContent = char;
            span.style.opacity = '0';
            element.appendChild(span);
        });

        // Typing animation
        const tl = gsap.timeline({
            delay: options.startDelay || 0.5,
            onComplete: () => setIsComplete(true),
        });

        tl.to(element.children, {
            opacity: 1,
            duration: 0.01,
            stagger: options.speed || 0.03,
            ease: 'none',
        });

        return () => {
            tl.kill();
        };
    }, [options.text, options.speed, options.startDelay, options.enabled]);

    return { elementRef, isComplete };
};
