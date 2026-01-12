import { Search } from "lucide-react";
import { useState } from "react";

const SearchBox = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");

    const handleKeyDown = (e: KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
            e.preventDefault();
            setIsOpen(true);
        }
        if (e.key === "Escape") {
            setIsOpen(false);
        }
    };

    useState(() => {
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    });

    return (
        <>
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary hover:bg-secondary/80 border border-border transition-colors"
            >
                <Search className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground hidden lg:inline">Search...</span>
            </button>

            {isOpen && (
                <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" onClick={() => setIsOpen(false)}>
                    <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl mx-auto px-4">
                        <div className="bg-card border border-border rounded-xl shadow-2xl" onClick={(e) => e.stopPropagation()}>
                            <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
                                <Search className="h-5 w-5 text-muted-foreground" />
                                <input
                                    type="text"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Search documentation..."
                                    className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground"
                                    autoFocus
                                />
                                <kbd className="px-2 py-1 text-xs text-muted-foreground bg-secondary rounded">ESC</kbd>
                            </div>
                            <div className="p-4">
                                <p className="text-sm text-muted-foreground text-center py-8">
                                    {query ? `No results for "${query}"` : "Start typing to search..."}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default SearchBox;
