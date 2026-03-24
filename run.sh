#!/bin/bash

echo "🚀 Starting VitalSync Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Resolve Firebase credentials path from .env (fallback to serviceAccountKey.json)
FIREBASE_CREDENTIALS_PATH="serviceAccountKey.json"
if [ -f ".env" ]; then
    ENV_PATH=$(grep -E '^FIREBASE_CREDENTIALS_PATH=' .env | tail -n 1 | cut -d'=' -f2-)
    ENV_PATH="${ENV_PATH//\"/}"
    if [ -n "$ENV_PATH" ]; then
        FIREBASE_CREDENTIALS_PATH="$ENV_PATH"
    fi
fi
FIREBASE_CREDENTIALS_PATH="${FIREBASE_CREDENTIALS_PATH#./}"

# Check for Firebase credentials
if [ ! -f "$FIREBASE_CREDENTIALS_PATH" ]; then
    echo "⚠️  Warning: $FIREBASE_CREDENTIALS_PATH not found!"
    echo "Please add your Firebase service account key before running."
    exit 1
fi

# Start server
echo ""
echo "✅ Starting server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
