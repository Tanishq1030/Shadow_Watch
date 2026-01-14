import { CodeBlock } from '@/components/docs/CodeBlock';
import { TableOfContents } from '@/components/docs/TableOfContents';
import { Key, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const tocItems = [
    { id: 'journey-story', title: 'From Trial to Production', level: 1 },
    { id: 'trial', title: 'Getting a Trial Key', level: 1 },
    { id: 'validation', title: 'License Validation', level: 1 },
    { id: 'production', title: 'Upgrading to Production', level: 1 },
];

export const LicenseManagement = () => {
    return (
        <div className="flex gap-8">
            <article className="flex-1">
                <div className="mb-12">
                    <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">
                        License Management
                    </h1>
                    <p className="text-xl text-zinc-400">
                        From trial to production
                    </p>
                </div>

                <section id="journey-story" className="mb-12">
                    <div className="bg-gradient-to-r from-emerald-500/10 to-transparent border-l-4 border-emerald-500 p-6 rounded-r-lg">
                        <p className="text-lg text-zinc-300 leading-relaxed">
                            You got your 30-day trial key. It works great. Now your CEO wants to buy.
                            Here's the license journey...
                        </p>
                    </div>
                </section>

                <section id="trial" className="mb-12">
                    <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                        <Key className="w-8 h-8 text-emerald-500" />
                        Getting a Trial Key
                    </h2>

                    <p className="text-zinc-300 mb-4">
                        Visit the license portal to generate a free 30-day trial:
                    </p>

                    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                        <Link
                            to="/get-license"
                            className="flex items-center gap-3 text-emerald-400 hover:text-emerald-300 font-bold"
                        >
                            <CheckCircle2 className="w-6 h-6" />
                            Generate Trial License
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <p className="text-sm text-zinc-400 mt-3">
                            Instant activation • No credit card required • 30 days unlimited
                        </p>
                    </div>
                </section>

                <section id="validation" className="mb-12">
                    <h2 className="text-3xl font-bold mb-6">License Validation</h2>

                    <p className="text-zinc-300 mb-4">
                        Shadow Watch validates licenses on initialization:
                    </p>

                    <CodeBlock
                        code={`from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="...",
    license_key="SM-TRIAL-YOUR-KEY-HERE"
)

# Validation happens automatically
# - Checks expiration
# - Verifies signature
# - Validates against license server`}
                        language="python"
                    />

                    <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                        <p className="text-sm text-blue-200">
                            <strong>Note:</strong> License validation requires internet connectivity on first use.
                            After cache, offline operation is supported for 7 days.
                        </p>
                    </div>
                </section>

                <section id="production" className="mb-12">
                    <h2 className="text-3xl font-bold mb-6">Upgrading to Production</h2>

                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                            <div className="text-2xl font-bold text-emerald-400 mb-2">Starter</div>
                            <div className="text-3xl font-bold text-white mb-4">$49<span className="text-sm text-zinc-400">/mo</span></div>
                            <ul className="space-y-2 text-sm text-zinc-300">
                                <li>• 100K events/month</li>
                                <li>• Email support</li>
                                <li>• 1 production instance</li>
                            </ul>
                        </div>

                        <div className="bg-emerald-900/20 border border-emerald-500 rounded-lg p-6">
                            <div className="text-2xl font-bold text-emerald-400 mb-2">Pro</div>
                            <div className="text-3xl font-bold text-white mb-4">$199<span className="text-sm text-zinc-400">/mo</span></div>
                            <ul className="space-y-2 text-sm text-zinc-300">
                                <li>• 1M events/month</li>
                                <li>• Priority support</li>
                                <li>• Unlimited instances</li>
                                <li>• Redis clustering</li>
                            </ul>
                        </div>

                        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                            <div className="text-2xl font-bold text-purple-400 mb-2">Enterprise</div>
                            <div className="text-3xl font-bold text-white mb-4">Custom</div>
                            <ul className="space-y-2 text-sm text-zinc-300">
                                <li>• Unlimited events</li>
                                <li>• 24/7 support</li>
                                <li>• SLA guarantee</li>
                                <li>• Custom integrations</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-6 text-center">
                        <p className="text-zinc-400 text-sm">
                            Contact: <a href="mailto:license@shadowwatch.dev" className="text-emerald-400 hover:underline">license@shadowwatch.dev</a>
                        </p>
                    </div>
                </section>
            </article>
            <TableOfContents items={tocItems} />
        </div>
    );
};
