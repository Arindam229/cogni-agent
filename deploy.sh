#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

echo "🚀 Starting Agent Deployment..."

# 1. Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin master  # Verify your branch name!

# 2. Setup/Update Virtual Environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating venv..."
source venv/bin/activate

# 3. Install Dependencies
echo "📦 Installing requirements..."
pip install -r requirements.txt

# 4. Restart PM2 Process
echo "Bg Restarting PM2 process..."
# Check if process exists in PM2
if pm2 list | grep -q "cogni-agent"; then
    pm2 restart cogni-agent
else
    pm2 start ecosystem.config.js
fi

echo "✅ Deployment Complete!"
