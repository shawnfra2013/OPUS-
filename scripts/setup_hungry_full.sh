#!/bin/bash
# DISABLED: Ollama-related full setup neutralized
# Original moved to a timestamped file and a backup copy placed in ~/cleanup_backups_<TIMESTAMP>
# To restore: move the backup back into place, for example:
#   mv ~/cleanup_backups_<TIMESTAMP>/setup_hungry_full.sh.bak.<TIMESTAMP> ~/hungry/setup_hungry_full.sh

echo "This script has been disabled to prevent automatic Ollama installs/starts."
echo "Backups were created in ~/cleanup_backups_* and originals were moved to *.disabled.*"
echo "If you intentionally want to re-enable, restore the original file from the backups."

exit 0
#!/bin/bash
set -e

# 1. Ensure Homebrew is installed
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
  exit 1
fi

# 2. Ensure Python 3 is installed
if ! command -v python3 &>/dev/null; then
  echo "Installing Python 3..."
  brew install python
fi

# 3. Ensure pip is available
if ! command -v pip3 &>/dev/null; then
  echo "pip3 not found. Installing pip..."
  python3 -m ensurepip --upgrade
fi

# 4. Ensure Ollama is installed
if ! command -v ollama &>/dev/null; then
  echo "Installing Ollama..."
  brew install ollama
fi

# 5. Install Python dependencies
pip3 install --upgrade ollama requests numpy torch transformers

# 6. Start Ollama server if not running
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 2
fi

# 7. Pull base model
ollama pull llama3.1:8b

# 8. Build uncensored model
ollama create uncensored-llama3 -f uncensored.Modelfile

echo
echo "✅ Hungry jailbreak environment is ready!"
echo "Run: python3 launch_jailbreak.py"
