#!/bin/bash

# Quick start script for FinWeave React Frontend

echo "🚀 Starting FinWeave React Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if backend is running (optional check)
echo "🔍 Checking backend connection..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:5001"
else
    echo "⚠️  Backend not detected at http://localhost:5001"
    echo "   Make sure your backend is running before connecting."
fi
echo ""

# Start dev server
echo "🌐 Starting development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""

npm run dev
