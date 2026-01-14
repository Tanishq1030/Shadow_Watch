import { useEffect, useRef, useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface CodeBlockProps {
    code: string;
    language?: string;
    filename?: string;
}

export const CodeBlock = ({ code, language = 'bash', filename }: CodeBlockProps) => {
    const [copied, setCopied] = useState(false);
    const codeRef = useRef<HTMLDivElement>(null);

    // Scroll animation
    useEffect(() => {
        if (!codeRef.current) return;

        const el = codeRef.current;
        const trigger = ScrollTrigger.create({
            trigger: el,
            start: 'top 70%',
            onEnter: () => {
                gsap.from(el, { opacity: 0, y: 30, duration: 0.6, ease: 'power2.out' });
            },
            once: true,
        });

        // Hover
        const onEnter = () => gsap.to(el, { scale: 1.01, boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)', duration: 0.3 });
        const onLeave = () => gsap.to(el, { scale: 1, boxShadow: 'none', duration: 0.3 });

        el.addEventListener('mouseenter', onEnter);
        el.addEventListener('mouseleave', onLeave);

        return () => {
            trigger.kill();
            el.removeEventListener('mouseenter', onEnter);
            el.removeEventListener('mouseleave', onLeave);
        };
    }, []);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        toast.success('Copied!');
        setTimeout(() => setCopied(false), 2000);
    };

    // VS Code Python syntax highlighting
    const highlightPython = (code: string) => {
        let result = code;

        // Keywords - Purple
        const keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'in', 'return', 'import', 'from', 'as', 'with', 'try', 'except', 'finally', 'async', 'await', 'lambda', 'yield'];
        keywords.forEach((kw) => {
            const regex = new RegExp(`\\b(${kw})\\b`, 'g');
            result = result.replace(regex, '<span style="color: #c586c0; font-weight: 600;">$1</span>');
        });

        // Built-in functions - Yellow
        const builtins = ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'open', 'input'];
        builtins.forEach((fn) => {
            const regex = new RegExp(`\\b(${fn})\\b`, 'g');
            result = result.replace(regex, '<span style="color: #dcdcaa;">$1</span>');
        });

        // Strings - Orange
        result = result.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, '<span style="color: #ce9178;">$&</span>');

        // Numbers - Light Green
        result = result.replace(/\b(\d+\.?\d*)\b/g, '<span style="color: #b5cea8;">$1</span>');

        // Comments - Gray/Green
        result = result.replace(/(#.*)/g, '<span style="color: #6a9955; font-style: italic;">$1</span>');

        // True/False/None - Light Blue
        result = result.replace(/\b(True|False|None)\b/g, '<span style="color: #569cd6;">$1</span>');

        return result;
    };

    return (
        <div ref={codeRef} className="relative group my-4 bg-black border border-zinc-800 rounded overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between bg-zinc-950 border-b border-zinc-800 px-4 py-2">
                <div className="flex items-center gap-2 font-mono text-base">
                    <span className="text-violet-400">$</span>
                    <span className="text-cyan-400">{filename || (language !== 'bash' ? 'output' : '')}</span>
                </div>
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-zinc-400 hover:text-violet-400 transition-colors rounded border border-zinc-800 hover:border-violet-500"
                >
                    {copied ? <><Check className="w-4 h-4" />Copied</> : <><Copy className="w-4 h-4" />Copy</>}
                </button>
            </div>

            {/* Code */}
            <pre className="p-6 overflow-x-auto">
                <code
                    className="font-mono text-base leading-relaxed"
                    style={{ color: '#d4d4d8' }}
                    dangerouslySetInnerHTML={{
                        __html: language === 'python' ? highlightPython(code) : code,
                    }}
                />
            </pre>
        </div>
    );
};
