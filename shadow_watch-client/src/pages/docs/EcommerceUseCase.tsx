import { CodeBlock } from '@/components/docs/CodeBlock';
import { Terminal, TerminalHeader, TerminalBody } from '@/components/docs/Terminal';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const EcommerceUseCase = () => {
    return (
        <div className="w-full">
            <article className="max-w-5xl mx-auto">
                <div className="mb-12">
                    <h1 className="mb-4">E-commerce Fraud Prevention</h1>
                    <p className="text-xl text-zinc-400">
                        Protecting ShopNow from account takeovers and fraud
                    </p>
                </div>

                <Terminal>
                    <TerminalBody mode="text">
                        <p className="text-zinc-300">
                            <span className="text-red-500">Problem:</span> ShopNow was losing $100K/month to fraudulent orders.
                            Attackers used stolen credentials to buy high-value electronics.
                        </p>
                        <p className="text-zinc-300 mt-3">
                            <span className="text-green-500">Solution:</span> Shadow Watch detected anomalous purchasing patterns in real-time.
                        </p>
                    </TerminalBody>
                </Terminal>

                <section className="mb-12">
                    <h2 className="mb-6">Track Product Views</h2>

                    <CodeBlock
                        code={`@app.get("/products/{product_id}")
async def view_product(product_id: str, user_id: int):
    # Track the view
    await sw.track(
        user_id=user_id,
        entity_id=product_id,
        action="view",
        metadata={
            "category": product.category,
            "price": product.price
        }
    )
    
    return product_details`}
                        language="python"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Track Add to Cart</h3>

                    <CodeBlock
                        code={`@app.post("/cart/add")
async def add_to_cart(product_id: str, user_id: int, quantity: int):
    await sw.track(
        user_id=user_id,
        entity_id=product_id,
        action="add_to_cart",
        metadata={
            "quantity": quantity,
            "price": get_price(product_id),
            "total": quantity * get_price(product_id)
        }
    )
    
    return {"status": "added"}`}
                        language="python"
                    />

                    <h3 className="text-xl font-bold mt-8 mb-4">Verify Checkout</h3>

                    <CodeBlock
                        code={`@app.post("/checkout")
async def checkout(cart: Cart, user_id: int, request: Request):
    # Calculate trust score
    trust = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.headers.get("x-device-id")
        }
    )
    
    # High-value orders need high trust
    order_total = sum(item.price * item.quantity for item in cart.items)
    
    if order_total > 1000 and trust["trust_score"] < 0.6:
        # Flag for manual review
        await flag_order_for_review(user_id, order_total, trust)
        return {"status": "pending_review"}
    
    if trust["action"] == "block":
        raise HTTPException(403, "Unable to process order")
    
    # Process order
    return await process_checkout(cart, user_id)`}
                        language="python"
                        filename="checkout.py"
                    />
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Results</h2>

                    <Terminal>
                        <TerminalHeader>
                            <span className="text-green-500">$</span> shopnow results --month 1
                        </TerminalHeader>
                        <TerminalBody mode="text">
                            <div className="space-y-3 font-mono text-sm">
                                <div className="text-green-500">✓ Fraudulent orders blocked: 127</div>
                                <div className="text-green-500">✓ Losses prevented: $89,400</div>
                                <div className="text-yellow-500">⚠ Orders flagged for review: 23</div>
                                <div className="text-zinc-500"># False positives: 2 (manually approved)</div>
                            </div>
                        </TerminalBody>
                    </Terminal>
                </section>

                <section className="mb-12">
                    <h2 className="mb-6">Next Steps</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <Link to="/docs/gaming-platform" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Gaming Platform Use Case
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">Bot detection in gaming</p>
                            </div>
                        </Link>

                        <Link to="/docs/social-media" className="group">
                            <div className="border border-zinc-900 bg-black p-6 rounded hover:border-green-500 transition-colors">
                                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                    Social Media Use Case
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-green-500" />
                                </h3>
                                <p className="text-sm text-zinc-400">Account safety</p>
                            </div>
                        </Link>
                    </div>
                </section>
            </article>
        </div>
    );
};
