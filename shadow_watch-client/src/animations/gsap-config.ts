import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// GSAP defaults for consistent animations
gsap.defaults({
    ease: 'power2.out',
    duration: 0.6,
});

// Easing curves
export const easing = {
    smooth: 'power2.out',
    snappy: 'power3.out',
    elastic: 'elastic.out(1, 0.5)',
    expo: 'expo.out',
};

// Animation timings
export const timing = {
    fast: 0.3,
    normal: 0.6,
    slow: 1.0,
    verySlow: 1.5,
};

// Scroll trigger defaults
export const scrollTriggerDefaults = {
    start: 'top 85%',
    toggleActions: 'play none none reverse',
};

// Fade in from bottom animation
export const fadeInUp = (element: HTMLElement, delay = 0) => {
    return gsap.from(element, {
        y: 40,
        opacity: 0,
        duration: timing.normal,
        delay,
        ease: easing.smooth,
    });
};

// Fade in with scale
export const fadeInScale = (element: HTMLElement, delay = 0) => {
    return gsap.from(element, {
        scale: 0.95,
        opacity: 0,
        duration: timing.normal,
        delay,
        ease: easing.smooth,
    });
};

// Stagger animation for multiple elements
export const staggerFadeIn = (elements: HTMLElement[], stagger = 0.1) => {
    return gsap.from(elements, {
        y: 30,
        opacity: 0,
        duration: timing.normal,
        stagger,
        ease: easing.smooth,
    });
};

// Glow effect on hover
export const glowOnHover = (element: HTMLElement) => {
    const onEnter = () => {
        gsap.to(element, {
            boxShadow: '0 0 20px rgba(34, 197, 94, 0.3), 0 0 40px rgba(34, 197, 94, 0.1)',
            duration: 0.3,
            ease: easing.smooth,
        });
    };

    const onLeave = () => {
        gsap.to(element, {
            boxShadow: '0 0 0px rgba(34, 197, 94, 0)',
            duration: 0.3,
            ease: easing.smooth,
        });
    };

    element.addEventListener('mouseenter', onEnter);
    element.addEventListener('mouseleave', onLeave);

    return () => {
        element.removeEventListener('mouseenter', onEnter);
        element.removeEventListener('mouseleave', onLeave);
    };
};

// Typing effect string splitting
export const typeWriter = (element: HTMLElement, text: string, speed = 0.05) => {
    const chars = text.split('');
    element.textContent = '';

    chars.forEach((char, i) => {
        const span = document.createElement('span');
        span.textContent = char;
        span.style.opacity = '0';
        element.appendChild(span);
    });

    return gsap.to(element.children, {
        opacity: 1,
        duration: 0.01,
        stagger: speed,
        ease: 'none',
    });
};

// Check if user prefers reduced motion
export const prefersReducedMotion = () => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// Safe animate - respects reduced motion
export const safeAnimate = (
    element: HTMLElement,
    animation: gsap.TweenVars,
    immediate = false
) => {
    if (prefersReducedMotion() || immediate) {
        return gsap.set(element, { ...animation, duration: 0 });
    }
    return gsap.to(element, animation);
};

export default gsap;
