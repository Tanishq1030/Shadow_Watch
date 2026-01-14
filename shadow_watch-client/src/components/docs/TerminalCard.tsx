import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';

interface TerminalCardProps {
    children: React.ReactNode;
    variant?: 'success' | 'warning' | 'error' | 'info' | 'default';
    glowIntensity?: 'low' | 'medium' | 'high';
    scanlines?: boolean;
}

const variantStyles = {
    success: {
        borderColor: 'border-emerald-500/50',
        glowColor: 'rgba(16, 185, 129, 0.3)',
        shadowColor: '0 0 30px rgba(16, 185, 129, 0.2)',
    },
    warning: {
        borderColor: 'border-amber-500/50',
        glowColor: 'rgba(245, 158, 11, 0.3)',
        shadowColor: '0 0 30px rgba(245, 158, 11, 0.2)',
    },
    error: {
        borderColor: 'border-red-500/50',
        glowColor: 'rgba(239, 68, 68, 0.3)',
        shadowColor: '0 0 30px rgba(239, 68, 68, 0.2)',
    },
    info: {
        borderColor: 'border-blue-500/50',
        glowColor: 'rgba(59, 130, 246, 0.3)',
        shadowColor: '0 0 30px rgba(59, 130, 246, 0.2)',
    },
    default: {
        borderColor: 'border-zinc-700/50',
        glowColor: 'rgba(113, 113, 122, 0.2)',
        shadowColor: '0 0 20px rgba(113, 113, 122, 0.1)',
    },
};

export const TerminalCard = ({
    children,
    variant = 'default',
    glowIntensity = 'medium',
    scanlines = true
}: TerminalCardProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const cardRef = useRef<HTMLDivElement>(null);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    const styles = variantStyles[variant];

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!cardRef.current) return;

            const rect = cardRef.current.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            setMousePosition({ x, y });
        };

        if (isHovered) {
            window.addEventListener('mousemove', handleMouseMove);
        }

        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, [isHovered]);

    return (
        <motion.div
            ref={cardRef}
            className={`relative bg-zinc-950 border ${styles.borderColor} rounded-lg p-6 overflow-hidden group`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            whileHover={{
                y: -4,
                transition: { duration: 0.3 }
            }}
            style={{
                boxShadow: isHovered ? styles.shadowColor : 'none',
            }}
        >
            {/* Cursor spotlight effect */}
            {isHovered && (
                <div
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                    style={{
                        background: `radial-gradient(600px circle at ${mousePosition.x}% ${mousePosition.y}%, ${styles.glowColor}, transparent 40%)`,
                    }}
                />
            )}

            {/* Scanline effect */}
            {scanlines && (
                <div className="absolute inset-0 pointer-events-none opacity-20">
                    <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(255,255,255,0.03)_2px,rgba(255,255,255,0.03)_4px)] animate-scanline" />
                </div>
            )}

            {/* Content */}
            <div className="relative z-10">
                {children}
            </div>

            {/* Glow border animation */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                <div className={`absolute inset-0 rounded-lg border-2 ${styles.borderColor} animate-pulse`} />
            </div>
        </motion.div>
    );
};

// Add to global CSS
const styles = `
@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

.animate-scanline {
  animation: scanline 8s linear infinite;
}
`;
