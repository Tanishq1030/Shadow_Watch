import { Star } from "lucide-react";
import { useEffect, useState } from "react";

const GitHubStars = () => {
    const [stars, setStars] = useState<number | null>(null);
    const repoUrl = "https://github.com/Tanishq1030/Shadow_Watch";

    useEffect(() => {
        const fetchStars = async () => {
            try {
                const response = await fetch("https://api.github.com/repos/Tanishq1030/Shadow_Watch");
                const data = await response.json();
                setStars(data.stargazers_count);
            } catch (error) {
                console.error("Failed to fetch GitHub stars:", error);
                setStars(0);
            }
        };

        fetchStars();
        // Refresh every 5 minutes
        const interval = setInterval(fetchStars, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <a
            href={repoUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary hover:bg-secondary/80 border border-border transition-colors"
        >
            <Star className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
                {stars !== null ? stars.toLocaleString() : "..."}
            </span>
        </a>
    );
};

export default GitHubStars;
