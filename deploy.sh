#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Navigate to script directory
cd "$(dirname "$0")"

echo "🚀 Starting Agent Deployment..."

# --- Python Environment Setup ---

BOOTSTRAP_DIR="$HOME/cogni_miniconda"
PYTHON_EXEC="python3"

# Check if we have a valid Python 3.9+
if command -v python3.11 &> /dev/null; then
    PYTHON_EXEC="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_EXEC="python3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_EXEC="python3.9"
fi

# Function to check version logic
check_python_version() {
    $1 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)' &> /dev/null
}

if ! check_python_version "$PYTHON_EXEC"; then
    echo "⚠️  System Python is too old or missing (Needs 3.9+)."
    
    # Check if we already installed Miniconda
    if [ -f "$BOOTSTRAP_DIR/bin/python3" ]; then
        echo "✅ Using existing Miniconda at $BOOTSTRAP_DIR"
        PYTHON_EXEC="$BOOTSTRAP_DIR/bin/python3"
    else
        echo "📦 Bootstrapping Miniconda (Local Python Installation)..."
        
        # Download Miniconda
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        
        # Install privately
        bash miniconda.sh -b -p "$BOOTSTRAP_DIR"
        rm miniconda.sh
        
        # Update path to use new python
        PYTHON_EXEC="$BOOTSTRAP_DIR/bin/python3"
        
        echo "✅ Miniconda installed!"
    fi
fi

echo "Using Python: $($PYTHON_EXEC --version)"

# --- Deployment ---

# 1. Pull latest changes
echo "📥 Pulling latest changes from main..."
git fetch origin
git reset --hard origin/main

# 2. Setup/Update Virtual Environment (using the good python)
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "🐍 Creating virtual environment..."
    rm -rf venv
    $PYTHON_EXEC -m venv venv
fi

echo "🔌 Activating venv..."
source venv/bin/activate

# 3. Install Dependencies
echo "📦 Installing requirements..."
pip install -r requirements.txt

# 4. Restart PM2 Process
echo "Bg Restarting PM2 process..."
if pm2 list | grep -q "cogni-agent"; then
    pm2 delete cogni-agent
fi

# Need to use the venv python explicitly for PM2 to persist correctly
pm2 start ecosystem.config.js --interpreter ./venv/bin/python

echo "✅ Deployment Complete!"
