#!/bin/bash
set -e

# 1. Activate Python venv and install dependencies
cd /Users/shawnfrahm/hungry
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install ollama requests numpy torch transformers

# 2. Build VS Code extension
cd /Users/shawnfrahm/hungry/local-agent-vscode
npm install
npx tsc -p ./

# 3. Launch Extension Development Host
echo "Launching VS Code Extension Development Host..."
code --extensionDevelopmentPath=/Users/shawnfrahm/hungry/local-agent-vscode &

echo ""
echo "✅ All setup steps complete!"
echo "Next steps:"
echo "1. In the Extension Development Host window, open the Command Palette (Cmd+Shift+P) and run: Local Agent: Open Panel"
echo "2. Use the chat panel to interact with your local agent."
echo ""
echo "If you see any errors, copy them here for troubleshooting."
