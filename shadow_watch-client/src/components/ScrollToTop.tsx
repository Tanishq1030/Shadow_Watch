import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import gsap from 'gsap';

interface ScrollToTopProps {
    mainRef: React.RefObject<HTMLElement>;
}

export const ScrollToTop = ({ mainRef }: ScrollToTopProps) => {
    const { pathname } = useLocation();

    useEffect(() => {
        // Instant scroll to top (no animation, no delay)
        window.scrollTo({ top: 0, behavior: 'instant' });

        // Fade in the new page
        if (mainRef.current) {
            gsap.fromTo(
                mainRef.current,
                { opacity: 0 },
                {
                    opacity: 1,
                    duration: 0.5,
                    ease: 'power2.out',
                    delay: 0.1,
                }
            );
        }
    }, [pathname, mainRef]);

    return null;
};
