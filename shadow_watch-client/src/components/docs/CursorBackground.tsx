import { useEffect } from 'react';

export const CursorBackground = () => {
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            const x = (e.clientX / window.innerWidth) * 100;
            const y = (e.clientY / window.innerHeight) * 100;

            document.documentElement.style.setProperty('--mouse-x', `${x}%`);
            document.documentElement.style.setProperty('--mouse-y', `${y}%`);
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <div className="fixed inset-0 pointer-events-none z-0">
            {/* Primary gradient following cursor */}
            <div
                className="absolute inset-0 opacity-30 transition-opacity duration-1000"
                style={{
                    background: `radial-gradient(800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(16, 185, 129, 0.15), transparent 50%)`
                }}
            />

            {/* Secondary gradient (offset) */}
            <div
                className="absolute inset-0 opacity-20"
                style={{
                    background: `radial-gradient(600px circle at calc(var(--mouse-x, 50%) + 10%) calc(var(--mouse-y, 50%) + 10%), rgba(59, 130, 246, 0.1), transparent 40%)`
                }}
            />

            {/* Ambient grid */}
            <div className="absolute inset-0 opacity-5">
                <div className="absolute inset-0"
                    style={{
                        backgroundImage: `
              linear-gradient(rgba(16, 185, 129, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(16, 185, 129, 0.1) 1px, transparent 1px)
            `,
                        backgroundSize: '50px 50px'
                    }}
                />
            </div>
        </div>
    );
};
