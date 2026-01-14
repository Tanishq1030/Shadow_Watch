import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';

export const ExtendingShadowWatch = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">Extending Shadow Watch</h1>
                    <p className="text-xl text-zinc-400">
                        Custom adapters, storage backends, and integrations
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            Need MongoDB? DynamoDB? Custom storage? Shadow Watch is <span className="text-green-500">extensible by design</span>.
                            Create custom adapters for any database or service.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Custom Storage Adapter</h2>

                    <p className="mb-4">Create a MongoDB adapter:</p>

                    <CodeBlock
                        code={`from shadowwatch.core.base import StorageAdapter
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Optional

class MongoDBAdapter(StorageAdapter):
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.shadowwatch
    
    async def store_activity(
        self,
        user_id: int,
        entity_id: str,
        action: str,
        metadata: Dict
    ):
        await self.db.activities.insert_one({
            "user_id": user_id,
            "entity_id": entity_id,
            "action": action,
            "metadata": metadata,
            "created_at": datetime.utcnow()
        })
    
    async def get_profile(self, user_id: int) -> Optional[Dict]:
        return await self.db.profiles.find_one({"user_id": user_id})
    
    async def update_profile(self, user_id: int, data: Dict):
        await self.db.profiles.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )`}
                        language="python"
                        filename="mongodb_adapter.py"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Use Custom Adapter</h3>

                    <CodeBlock
                        code={`from shadowwatch import ShadowWatch
from my_adapters import MongoDBAdapter

sw = ShadowWatch(
    storage_adapter=MongoDBAdapter("mongodb://localhost:27017"),
    license_key="SW-TRIAL-..."
)

# Works the same!
await sw.track(user_id=42, entity_id="product", action="view")`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Custom Middleware</h2>

                    <CodeBlock
                        code={`from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomShadowWatchMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, shadow_watch, custom_rules):
        super().__init__(app)
        self.sw = shadow_watch
        self.rules = custom_rules
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Custom tracking logic
        if self.should_track(request):
            await self.sw.track(
                user_id=get_user(request),
                entity_id=extract_entity(request),
                action=determine_action(request)
            )
        
        return response
    
    def should_track(self, request: Request) -> bool:
        # Your custom rules
        return request.url.path.startswith("/api/")

app.add_middleware(
    CustomShadowWatchMiddleware,
    shadow_watch=sw,
    custom_rules={"track_admin": False}
)`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Custom Scoring Algorithm</h2>

                    <CodeBlock
                        code={`from shadowwatch.core.scorer import TrustScoreCalculator

class CustomTrustScorer(TrustScoreCalculator):
    async def calculate_score(
        self,
        user_id: int,
        context: Dict
    ) -> float:
        # Get base score
        base_score = await super().calculate_score(user_id, context)
        
        # Add custom factors
        if context.get("is_vip_customer"):
            base_score += 0.1  # Boost VIPs
        
        if context.get("recent_fraud_reports") > 0:
            base_score -= 0.3  # Penalize flagged users
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, base_score))

# Use custom scorer
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    trust_scorer=CustomTrustScorer()
)`}
                        language="python"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Event Hooks</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shadowwatch hooks --available
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="font-mono text-sm space-y-1">
                                <div className="text-zinc-400">on_track_before</div>
                                <div className="text-zinc-400">on_track_after</div>
                                <div className="text-zinc-400">on_profile_update</div>
                                <div className="text-zinc-400">on_trust_score_calculated</div>
                                <div className="text-zinc-400">on_anomaly_detected</div>
                            </div>
                        </TerminalBody>
                    </Terminal>

                    <CodeBlock
                        code={`sw = ShadowWatch(...)

@sw.on("on_anomaly_detected")
async def send_alert(user_id: int, anomaly_type: str, score: float):
    if score < 0.3:
        await send_email_to_security_team(
            f"High-risk login detected for user {user_id}"
        )
        await send_sms_to_user(user_id, "Suspicious activity detected")

@sw.on("on_profile_update")
async def log_to_analytics(user_id: int, changes: Dict):
    await analytics.track("profile_updated", {
        "user_id": user_id,
        "changes": changes
    })`}
                        language="python"
                    />
                </section>
            </article>
        </div>
    );
};
