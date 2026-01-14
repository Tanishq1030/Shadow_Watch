import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Activity {
    symbol: string;
    count: number;
}

export const EntropyCalculator = () => {
    const [activities, setActivities] = useState<Activity[]>([
        { symbol: 'AAPL', count: 3 },
        { symbol: 'GOOGL', count: 2 },
        { symbol: 'MSFT', count: 2 },
        { symbol: 'TSLA', count: 1 },
        { symbol: 'META', count: 1 },
        { symbol: 'NVDA', count: 1 },
    ]);

    const calculateEntropy = () => {
        const total = activities.reduce((sum, a) => sum + a.count, 0);
        if (total === 0) return 0;

        let entropy = 0;
        activities.forEach(activity => {
            if (activity.count > 0) {
                const p = activity.count / total;
                entropy -= p * Math.log2(p);
            }
        });

        // Normalize to 0-1 scale
        const maxEntropy = Math.log2(activities.length);
        return maxEntropy > 0 ? entropy / maxEntropy : 0;
    };

    const addActivity = () => {
        setActivities([...activities, { symbol: `SYM${activities.length + 1}`, count: 1 }]);
    };

    const updateCount = (index: number, delta: number) => {
        const updated = [...activities];
        updated[index].count = Math.max(0, updated[index].count + delta);
        setActivities(updated);
    };

    const resetToHuman = () => {
        setActivities([
            { symbol: 'Python', count: 8 },
            { symbol: 'JavaScript', count: 3 },
            { symbol: 'TypeScript', count: 2 },
            { symbol: 'Rust', count: 1 },
        ]);
    };

    const resetToBot = () => {
        setActivities([
            { symbol: 'A', count: 1 },
            { symbol: 'B', count: 1 },
            { symbol: 'C', count: 1 },
            { symbol: 'D', count: 1 },
            { symbol: 'E', count: 1 },
            { symbol: 'F', count: 1 },
            { symbol: 'G', count: 1 },
            { symbol: 'H', count: 1 },
        ]);
    };

    const entropy = calculateEntropy();
    const isHumanLike = entropy < 0.6;
    const isBotLike = entropy > 0.9;

    const chartData = activities.map(a => ({
        name: a.symbol,
        count: a.count,
    }));

    return (
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-8">
            <h3 className="text-2xl font-bold text-white mb-6">🧮 Interactive Entropy Calculator</h3>

            <div className="grid md:grid-cols-2 gap-8">
                {/* Chart */}
                <div>
                    <h4 className="text-lg font-semibold text-white mb-4">Activity Distribution</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                            <XAxis dataKey="name" stroke="#71717a" />
                            <YAxis stroke="#71717a" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Bar dataKey="count" fill={isHumanLike ? '#10b981' : isBotLike ? '#ef4444' : '#f59e0b'} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Controls */}
                <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-white mb-4">Edit Activities</h4>

                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {activities.map((activity, index) => (
                            <div key={index} className="flex items-center gap-3 bg-zinc-900 rounded p-3">
                                <span className="text-white font-mono flex-1">{activity.symbol}</span>
                                <button
                                    onClick={() => updateCount(index, -1)}
                                    className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors"
                                >
                                    -
                                </button>
                                <span className="text-white font-mono w-8 text-center">{activity.count}</span>
                                <button
                                    onClick={() => updateCount(index, 1)}
                                    className="px-3 py-1 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded transition-colors"
                                >
                                    +
                                </button>
                            </div>
                        ))}
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={addActivity}
                            className="flex-1 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded transition-colors"
                        >
                            Add Activity
                        </button>
                        <button
                            onClick={resetToHuman}
                            className="flex-1 px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded transition-colors"
                        >
                            Human Pattern
                        </button>
                        <button
                            onClick={resetToBot}
                            className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors"
                        >
                            Bot Pattern
                        </button>
                    </div>
                </div>
            </div>

            {/* Result */}
            <div className="mt-8 border-t border-zinc-800 pt-6">
                <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-zinc-900 rounded-lg p-6 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Entropy Score</div>
                        <motion.div
                            className="text-5xl font-bold font-mono"
                            animate={{
                                color: isHumanLike ? '#10b981' : isBotLike ? '#ef4444' : '#f59e0b'
                            }}
                        >
                            {entropy.toFixed(3)}
                        </motion.div>
                    </div>

                    <div className="bg-zinc-900 rounded-lg p-6 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Pattern Type</div>
                        <div className={`text-2xl font-bold uppercase ${isHumanLike ? 'text-emerald-400' : isBotLike ? 'text-red-400' : 'text-yellow-400'
                            }`}>
                            {isHumanLike ? 'Human-like' : isBotLike ? 'Bot-like' : 'Suspicious'}
                        </div>
                    </div>

                    <div className="bg-zinc-900 rounded-lg p-6 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Interpretation</div>
                        <div className="text-sm text-zinc-300">
                            {isHumanLike && 'Structured pattern detected'}
                            {isBotLike && 'Random/mechanical behavior'}
                            {!isHumanLike && !isBotLike && 'Moderate uncertainty'}
                        </div>
                    </div>
                </div>

                {/* Formula */}
                <div className="mt-6 bg-black rounded-lg p-4 font-mono text-sm">
                    <div className="text-emerald-400 mb-2">// Shannon Entropy Formula</div>
                    <div className="text-blue-400">H(X) = -Σ p(x) · log₂(p(x))</div>
                    <div className="text-zinc-500 mt-2">// Normalized: {entropy.toFixed(3)} / {Math.log2(activities.length).toFixed(3)}</div>
                </div>
            </div>
        </div>
    );
};
