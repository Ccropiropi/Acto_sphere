#!/bin/bash

# Configuration
LOG_FILE="../dat/logs/git_automator.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$TIMESTAMP] Starting Auto-Commit Check..." >> "$LOG_FILE"

# Check for changes
if [[ -n $(git status -s) ]]; then
    echo "[$TIMESTAMP] Changes detected." >> "$LOG_FILE"
    
    # Add all changes
    git add .
    
    # Commit with timestamp
    COMMIT_MSG="Auto-commit: Update ecosystem state at $TIMESTAMP"
    git commit -m "$COMMIT_MSG"
    
    if [ $? -eq 0 ]; then
        echo "[$TIMESTAMP] Successfully committed: $COMMIT_MSG" >> "$LOG_FILE"
        echo "Changes committed successfully."
    else
        echo "[$TIMESTAMP] Error during commit." >> "$LOG_FILE"
        echo "Error: Commit failed."
    fi
else
    echo "[$TIMESTAMP] No changes detected. Skipping commit." >> "$LOG_FILE"
    echo "No changes to commit."
fi
