import { Link, useLocation } from 'react-router-dom';
import { ChevronDown, ChevronRight, Menu, X } from 'lucide-react';
import { useState } from 'react';

interface NavSection {
    title: string;
    icon: string;
    pages: { title: string; path: string }[];
}

const navSections: NavSection[] = [
    {
        title: 'Intelligence Hub',
        icon: '🎯',
        pages: [
            { title: 'Getting Started', path: '/docs/getting-started' },
            { title: 'What is Behavioral Intelligence?', path: '/docs/behavioral-intelligence' },
            { title: 'Installation & Quick Start', path: '/docs/installation' },
            { title: 'Core Concepts', path: '/docs/core-concepts' },
        ],
    },
    {
        title: 'Deploy Watchers',
        icon: '🚀',
        pages: [
            { title: 'FastAPI Integration', path: '/docs/fastapi-integration' },
            { title: 'Standalone Usage', path: '/docs/standalone-usage' },
            { title: 'E-commerce Use Case', path: '/docs/ecommerce' },
            { title: 'Gaming Platform', path: '/docs/gaming' },
            { title: 'Social Media', path: '/docs/social-media' },
        ],
    },
    {
        title: 'Memory Vault',
        icon: '💾',
        pages: [
            { title: 'PostgreSQL Setup', path: '/docs/postgresql' },
            { title: 'Redis Caching', path: '/docs/redis' },
            { title: 'MySQL Configuration', path: '/docs/mysql' },
            { title: 'Extending Shadow Watch', path: '/docs/extending' },
        ],
    },
    {
        title: 'Mastery',
        icon: '🔬',
        pages: [
            { title: 'Entropy Engine', path: '/docs/entropy-engine' },
            { title: 'Fingerprint Verification', path: '/docs/fingerprint-verification' },
            { title: 'Trust Score Algorithm', path: '/docs/trust-score' },
            { title: 'License Management', path: '/docs/license-management' },
        ],
    },
];

export const DocsSidebar = () => {
    const location = useLocation();
    const [expandedSections, setExpandedSections] = useState<string[]>(['Intelligence Hub']);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const toggleSection = (title: string) => {
        setExpandedSections((prev) =>
            prev.includes(title)
                ? prev.filter((t) => t !== title)
                : [...prev, title]
        );
    };

    const closeMobileMenu = () => setMobileMenuOpen(false);

    const SidebarContent = () => (
        <div className="p-4 md:p-6">
            <h2 className="text-lg font-bold text-white mb-6">Documentation</h2>

            {navSections.map((section) => (
                <div key={section.title} className="mb-6">
                    <button
                        onClick={() => toggleSection(section.title)}
                        className="flex items-center justify-between w-full text-sm font-semibold text-zinc-400 hover:text-white transition-colors mb-2"
                    >
                        <span className="flex items-center gap-2">
                            <span>{section.icon}</span>
                            <span>{section.title}</span>
                        </span>
                        {expandedSections.includes(section.title) ? (
                            <ChevronDown className="w-4 h-4" />
                        ) : (
                            <ChevronRight className="w-4 h-4" />
                        )}
                    </button>

                    {expandedSections.includes(section.title) && (
                        <ul className="ml-4 md:ml-6 space-y-1">
                            {section.pages.map((page) => (
                                <li key={page.path}>
                                    <Link
                                        to={page.path}
                                        onClick={closeMobileMenu}
                                        className={`block text-sm py-1.5 px-3 rounded transition-colors ${location.pathname === page.path
                                                ? 'bg-zinc-800 text-white font-medium'
                                                : 'text-zinc-500 hover:text-white hover:bg-zinc-900'
                                            }`}
                                    >
                                        {page.title}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            ))}
        </div>
    );

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setMobileMenuOpen(true)}
                className="md:hidden fixed top-4 left-4 z-50 p-2 bg-zinc-900 border border-zinc-800 rounded text-white hover:bg-zinc-800 transition-colors"
                aria-label="Open menu"
            >
                <Menu className="w-6 h-6" />
            </button>

            {/* Desktop Sidebar */}
            <aside className="hidden md:block w-64 border-r border-zinc-800 bg-zinc-950 h-screen sticky top-0 overflow-y-auto">
                <SidebarContent />
            </aside>

            {/* Mobile Sidebar Overlay */}
            {mobileMenuOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="md:hidden fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
                        onClick={closeMobileMenu}
                    />

                    {/* Sidebar */}
                    <aside className="md:hidden fixed left-0 top-0 bottom-0 w-72 bg-zinc-950 border-r border-zinc-800 z-50 overflow-y-auto">
                        {/* Close Button */}
                        <button
                            onClick={closeMobileMenu}
                            className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-white transition-colors"
                            aria-label="Close menu"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <SidebarContent />
                    </aside>
                </>
            )}
        </>
    );
};
