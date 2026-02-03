#!/bin/bash
# Full reset: Kill all services and restart
# Usage: ./AI-R

echo "🔄 Full system reset and restart..."
echo ""

cd "$(dirname "$0")"

echo "[1/3] Stopping all services..."
pkill -f run_agent.py 2>/dev/null || true
pkill -x ollama 2>/dev/null || true
echo "     ✅ Services stopped"

echo "[2/3] Waiting for clean shutdown..."
sleep 3

echo "[3/3] Restarting services..."
./AI-
