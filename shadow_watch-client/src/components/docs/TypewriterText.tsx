import { useState, useEffect } from 'react';

interface TypewriterTextProps {
    text: string;
    speed?: number;
    showCursor?: boolean;
    onComplete?: () => void;
}

export const TypewriterText = ({
    text,
    speed = 30,
    showCursor = true,
    onComplete
}: TypewriterTextProps) => {
    const [displayText, setDisplayText] = useState('');
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        setDisplayText('');
        setIsComplete(false);

        let index = 0;
        const timer = setInterval(() => {
            setDisplayText(text.slice(0, index + 1));
            index++;

            if (index >= text.length) {
                clearInterval(timer);
                setIsComplete(true);
                onComplete?.();
            }
        }, speed);

        return () => clearInterval(timer);
    }, [text, speed, onComplete]);

    return (
        <span className="font-mono text-emerald-400">
            {displayText}
            {showCursor && !isComplete && (
                <span className="inline-block w-2 h-5 bg-emerald-400 ml-1 animate-pulse">▋</span>
            )}
        </span>
    );
};
