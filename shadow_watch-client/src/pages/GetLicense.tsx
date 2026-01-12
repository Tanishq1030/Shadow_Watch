import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/AuthContext";
import ScrollReveal from "@/components/ScrollReveal";
import { Copy, Check, Key } from "lucide-react";
import { toast } from "sonner";

const GetLicense = () => {
    const navigate = useNavigate();
    const { user } = useAuth(); // We still check if a user is logged in to pre-fill, but it's not required
    const [licenseKey, setLicenseKey] = useState("");
    const [isCopied, setIsCopied] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    // Guest form state
    const [formData, setFormData] = useState({
        name: user?.name || "",
        email: user?.email || "",
        organization: user?.organization || "",
    });

    // Update form if user logs in/out
    useEffect(() => {
        if (user) {
            setFormData({
                name: user.name,
                email: user.email,
                organization: user.organization,
            });
        }
    }, [user]);

    const generateLicense = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();

        if (!formData.name || !formData.email || !formData.organization) {
            toast.error("Please fill in all fields.");
            return;
        }

        setIsGenerating(true);

        try {
            const response = await fetch("https://shadow-watch-guxu.vercel.app/trial", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: formData.name,
                    email: formData.email,
                    company: formData.organization,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Server Error (${response.status}):`, errorText);
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                setLicenseKey(data.license_key);
                toast.success("License key generated successfully!");
            } else {
                toast.error("Failed to generate license. Please try again.");
                console.error("License generation failed:", data);
            }
        } catch (error: any) {
            console.error("Fetch error details:", error);
            toast.error(error.message === "Failed to fetch" ? "Network error: Connection refused or timeout." : `Server error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(licenseKey);
        setIsCopied(true);
        toast.success("Copied to clipboard!");
        setTimeout(() => setIsCopied(false), 2000);
    };

    return (
        <div className="min-h-screen pt-24 pb-12 flex items-center justify-center px-4 bg-background overflow-hidden relative">
            <div className="absolute top-[-20%] left-[20%] w-[600px] h-[600px] rounded-full bg-emerald-500/5 blur-[120px] pointer-events-none" />

            <ScrollReveal className="max-w-2xl w-full">
                <div className="bg-card/50 backdrop-blur-xl border border-border/50 rounded-2xl p-8 shadow-xl">
                    <div className="text-center mb-10">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary mb-4">
                            <Key className="h-6 w-6" />
                        </div>
                        <h1 className="text-3xl font-bold mb-2">Get Your License Key</h1>
                        <p className="text-muted-foreground">
                            {licenseKey ? "Your 30-day trial key is ready!" : "Fill in your details to generate a 30-day trial key"}
                        </p>
                    </div>

                    {!licenseKey ? (
                        <form onSubmit={generateLicense} className="space-y-6 mb-8">
                            <div className="grid gap-6 md:grid-cols-2">
                                <div className="space-y-2">
                                    <Label htmlFor="name">Full Name</Label>
                                    <Input
                                        id="name"
                                        placeholder="Tanishq Dasari"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="organization">Organization</Label>
                                    <Input
                                        id="organization"
                                        placeholder="Google"
                                        value={formData.organization}
                                        onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="space-y-2 md:col-span-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="artisanecho@gmail.com"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                size="lg"
                                className="w-full h-12 text-base font-semibold"
                                disabled={isGenerating}
                            >
                                {isGenerating ? "Generating Key..." : "Generate 30-Day Trial Key"}
                            </Button>
                        </form>
                    ) : (
                        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <Label className="text-base text-primary font-medium">Your Trial License Key</Label>
                            <div className="relative group">
                                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="relative flex items-center">
                                    <Input
                                        readOnly
                                        value={licenseKey}
                                        className="h-14 font-mono text-lg tracking-wider text-center bg-background/80 border-primary/50 text-foreground"
                                    />
                                    <Button
                                        size="icon"
                                        className="absolute right-2 top-2 h-10 w-10 shrink-0"
                                        variant="ghost"
                                        onClick={copyToClipboard}
                                    >
                                        {isCopied ? <Check className="h-5 w-5 text-green-500" /> : <Copy className="h-5 w-5" />}
                                    </Button>
                                </div>
                            </div>
                            <p className="text-center text-sm text-muted-foreground mt-4">
                                Valid for 30 days. Need a production key? <Link to="/contact" className="text-primary hover:underline">Contact Sales</Link>
                            </p>
                        </div>
                    )}
                </div>

                {/* Live Server Stats (Verification) */}
                <div className="mt-8 grid grid-cols-3 gap-4 pb-8">
                    <ServerStat label="Active Licenses" endpoint="/stats" dataKey="total_licenses" />
                    <ServerStat label="Active Trials" endpoint="/stats" dataKey="active_trials" />
                    <ServerStat label="Events Tracked" endpoint="/stats" dataKey="total_events_tracked" />
                </div>
            </ScrollReveal>
        </div>
    );
};

const ServerStat = ({ label, endpoint, dataKey }: { label: string, endpoint: string, dataKey: string }) => {
    const [value, setValue] = useState<string | number>("-");

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch(`https://shadow-watch-guxu.vercel.app${endpoint}`);
                if (res.ok) {
                    const data = await res.json();
                    setValue(data[dataKey] || 0);
                }
            } catch (err) {
                console.error("Failed to fetch stats");
            }
        };
        fetchStats();
    }, [endpoint, dataKey]);

    return (
        <div className="bg-card/30 border border-border/30 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold font-mono">{value}</div>
            <div className="text-xs text-muted-foreground uppercase tracking-wider mt-1">{label}</div>
        </div>
    );
};

export default GetLicense;
