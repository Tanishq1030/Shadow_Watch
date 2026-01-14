import { useState } from 'react';
import { motion } from 'framer-motion';
import { Slider } from '@/components/ui/slider';

interface TrustScoreFactor {
    name: string;
    weight: number;
    value: number;
    description: string;
    color: string;
}

export const TrustScoreCalculator = () => {
    const [factors, setFactors] = useState<TrustScoreFactor[]>([
        {
            name: 'Fingerprint Match',
            weight: 0.4,
            value: 0.92,
            description: 'Does the behavioral pattern match?',
            color: 'bg-blue-500'
        },
        {
            name: 'Location Consistency',
            weight: 0.2,
            value: 0.95,
            description: 'Is this a known location?',
            color: 'bg-purple-500'
        },
        {
            name: 'Time Pattern',
            weight: 0.2,
            value: 0.88,
            description: 'Normal activity hours?',
            color: 'bg-yellow-500'
        },
        {
            name: 'Velocity Check',
            weight: 0.1,
            value: 1.0,
            description: 'Impossible travel?',
            color: 'bg-red-500'
        },
        {
            name: 'Device Familiarity',
            weight: 0.1,
            value: 0.85,
            description: 'Known device?',
            color: 'bg-pink-500'
        }
    ]);

    const calculateTrustScore = () => {
        return factors.reduce((sum, factor) => sum + (factor.value * factor.weight), 0);
    };

    const updateFactor = (index: number, newValue: number) => {
        const updated = [...factors];
        updated[index].value = newValue / 100;
        setFactors(updated);
    };

    const trustScore = calculateTrustScore();
    const riskLevel = trustScore >= 0.8 ? 'low' : trustScore >= 0.6 ? 'medium' : trustScore >= 0.3 ? 'high' : 'critical';
    const action = trustScore >= 0.8 ? 'allow' : trustScore >= 0.6 ? 'monitor' : trustScore >= 0.3 ? 'require_mfa' : 'block';

    const actionColors = {
        allow: 'text-emerald-400 border-emerald-500',
        monitor: 'text-yellow-400 border-yellow-500',
        require_mfa: 'text-orange-400 border-orange-500',
        block: 'text-red-400 border-red-500'
    };

    return (
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-8">
            <h3 className="text-2xl font-bold text-white mb-6">🎯 Interactive Trust Score Calculator</h3>

            {/* Factors */}
            <div className="space-y-6 mb-8">
                {factors.map((factor, index) => (
                    <div key={factor.name} className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-white font-semibold">{factor.name}</span>
                            <span className="text-zinc-400 text-sm">Weight: {(factor.weight * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Slider
                                value={[factor.value * 100]}
                                onValueChange={(value) => updateFactor(index, value[0])}
                                max={100}
                                step={1}
                                className="flex-1"
                            />
                            <span className="text-white font-mono w-12 text-right">
                                {factor.value.toFixed(2)}
                            </span>
                        </div>
                        <p className="text-zinc-500 text-sm">{factor.description}</p>

                        {/* Visual bar */}
                        <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                            <motion.div
                                className={`h-full ${factor.color}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${factor.value * 100}%` }}
                                transition={{ duration: 0.3 }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            {/* Result */}
            <div className="border-t border-zinc-800 pt-6">
                <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-zinc-900 rounded-lg p-4 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Trust Score</div>
                        <div className="text-4xl font-bold text-white font-mono">
                            {trustScore.toFixed(2)}
                        </div>
                    </div>

                    <div className="bg-zinc-900 rounded-lg p-4 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Risk Level</div>
                        <div className={`text-2xl font-bold uppercase ${riskLevel === 'low' ? 'text-emerald-400' :
                                riskLevel === 'medium' ? 'text-yellow-400' :
                                    riskLevel === 'high' ? 'text-orange-400' :
                                        'text-red-400'
                            }`}>
                            {riskLevel}
                        </div>
                    </div>

                    <div className="bg-zinc-900 rounded-lg p-4 text-center">
                        <div className="text-sm text-zinc-500 mb-2">Recommended Action</div>
                        <div className={`text-lg font-bold uppercase border-2 rounded px-3 py-1 inline-block ${actionColors[action]}`}>
                            {action.replace('_', ' ')}
                        </div>
                    </div>
                </div>

                {/* Code output */}
                <div className="mt-6 bg-black rounded-lg p-4 font-mono text-sm">
                    <div className="text-emerald-400">{`{`}</div>
                    <div className="ml-4 text-blue-400">"trust_score": {trustScore.toFixed(2)},</div>
                    <div className="ml-4 text-purple-400">"risk_level": "{riskLevel}",</div>
                    <div className="ml-4 text-yellow-400">"action": "{action}"</div>
                    <div className="text-emerald-400">{`}`}</div>
                </div>
            </div>
        </div>
    );
};
