#!/bin/bash
# Deploy Shadow Watch License Server to Fly.io
# Usage: chmod +x deploy.sh && ./deploy.sh

set -e  # Exit on error

echo "🚀 Deploying Shadow Watch License Server to Fly.io..."

# Check if Fly CLI is installed
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    echo "✅ Fly CLI installed"
fi

# Login to Fly.io
echo "🔐 Logging in to Fly.io..."
flyctl auth login

# Initialize Fly.io app (if not already done)
if [ ! -f fly.toml ]; then
    echo "📝 Initializing Fly.io app..."
    flyctl launch \
        --name shadowwatch-license \
        --region ord \
        --no-deploy \
        --org personal
fi

# Create persistent volume for SQLite
echo "💾 Creating persistent volume..."
if ! flyctl volumes list | grep -q "license_data"; then
    flyctl volumes create license_data --size 1 --region ord
    echo "✅ Volume created"
else
    echo "ℹ️  Volume already exists"
fi

# Deploy to Fly.io
echo "🚢 Deploying application..."
flyctl deploy

# Show deployment info
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your license server URL:"
flyctl info | grep "Hostname" | awk '{print "   https://" $2}'

echo ""
echo "🔑 Next steps:"
echo "   1. Generate trial keys:"
echo "      flyctl ssh console -C 'python generate_trial_keys.py'"
echo ""
echo "   2. Test health check:"
echo "      curl https://shadowwatch-license.fly.dev/"
echo ""
echo "   3. Update Shadow Watch library:"
echo "      Update shadowwatch/utils/license.py with your Fly.io URL"
