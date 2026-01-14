import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { scrollTriggerDefaults, fadeInUp, prefersReducedMotion } from '@/animations/gsap-config';

gsap.registerPlugin(ScrollTrigger);

interface UseScrollAnimationOptions {
    delay?: number;
    start?: string;
    disabled?: boolean;
}

export const useScrollAnimation = (options: UseScrollAnimationOptions = {}) => {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!elementRef.current || prefersReducedMotion() || options.disabled) {
            return;
        }

        const element = elementRef.current;

        // Animate on scroll
        const animation = fadeInUp(element, options.delay || 0);

        ScrollTrigger.create({
            trigger: element,
            animation,
            ...scrollTriggerDefaults,
            start: options.start || scrollTriggerDefaults.start,
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === element) {
                    trigger.kill();
                }
            });
        };
    }, [options.delay, options.start, options.disabled]);

    return elementRef;
};

export const useStaggerAnimation = (itemCount: number, stagger = 0.1) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current || prefersReducedMotion()) {
            return;
        }

        const container = containerRef.current;
        const items = Array.from(container.children) as HTMLElement[];

        if (items.length === 0) return;

        const animation = gsap.from(items, {
            y: 30,
            opacity: 0,
            duration: 0.6,
            stagger,
            ease: 'power2.out',
        });

        ScrollTrigger.create({
            trigger: container,
            animation,
            ...scrollTriggerDefaults,
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === container) {
                    trigger.kill();
                }
            });
        };
    }, [itemCount, stagger]);

    return containerRef;
};
