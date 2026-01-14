interface TOCItem {
    id: string;
    title: string;
    level: number;
}

interface TableOfContentsProps {
    items: TOCItem[];
}

export const TableOfContents = ({ items }: TableOfContentsProps) => {
    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    return (
        <aside className="w-64 border-l border-zinc-800 h-screen sticky top-0 overflow-y-auto hidden xl:block">
            <div className="p-6">
                <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">
                    On This Page
                </h3>
                <ul className="space-y-2">
                    {items.map((item) => (
                        <li
                            key={item.id}
                            style={{ paddingLeft: `${(item.level - 1) * 12}px` }}
                        >
                            <button
                                onClick={() => scrollToSection(item.id)}
                                className="text-sm text-zinc-500 hover:text-white transition-colors text-left w-full"
                            >
                                {item.title}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </aside>
    );
};
