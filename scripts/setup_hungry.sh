#!/bin/bash
# DISABLED: Ollama-related setup neutralized
# Original moved to a timestamped file and a backup copy placed in ~/cleanup_backups_<TIMESTAMP>
# To restore: move the backup back into place, for example:
#   mv ~/cleanup_backups_<TIMESTAMP>/setup_hungry.sh.bak.<TIMESTAMP> ~/hungry/setup_hungry.sh

echo "This script has been disabled to prevent automatic Ollama installs/starts."
echo "Backups were created in ~/cleanup_backups_* and originals were moved to *.disabled.*"
echo "If you intentionally want to re-enable, restore the original file from the backups."

exit 0
#!/bin/bash
# Auto-setup script for hungry jailbreak LLM environment
set -e

# Step 1: Install Python dependencies
pip install ollama requests numpy torch transformers

# Step 2: Start Ollama (if not running)
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 2
fi

# Step 3: Pull base model
ollama pull llama3.1:8b

# Step 4: Build uncensored model
ollama create uncensored-llama3 -f uncensored.Modelfile

# Step 5: Ready to run
cat <<EOF

✅ Hungry jailbreak environment is ready!
Run: python launch_jailbreak.py
EOF
