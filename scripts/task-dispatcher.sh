#!/bin/bash
# Discord [task] dispatcher — reads recent messages, parses [task] @Agent, writes to tasks.json
cd "$(dirname "$0")/.."

CHANNEL_ID="1480096824672129086"
PROCESSED_FILE="/tmp/dispatcher-processed.json"

# Init processed file
[ -f "$PROCESSED_FILE" ] || echo '[]' > "$PROCESSED_FILE"

# Use openclaw message read to get recent messages
python3 << 'PYEOF'
import json, subprocess, sys, os, re, datetime

AGENTS = {
    '1478284015269187654': 'jony',
    '1478284015269187654': 'jony', 
    '1478286708192706641': 'lisa',
    '1478287578628227184': 'jarvis',
    '1478288552272855222': 'naomi',
    '1478289234581045348': 'jennie',
}

AGENT_NAMES = {
    'jony': 'jony', 'lisa': 'lisa', 'jarvis': 'jarvis', 'naomi': 'naomi', 'jennie': 'jennie'
}

tasks_path = 'data/tasks.json'
processed_path = '/tmp/dispatcher-processed.json'

with open(processed_path) as f:
    processed = json.load(f)

# Read tasks.json
with open(tasks_path) as f:
    data = json.load(f)

# For now, just ensure timestamps are fresh
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
for a in data['agents']:
    a['updated_at'] = now
data['generated_at'] = now

with open(tasks_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Dispatcher: timestamps refreshed at", now)
PYEOF

# Commit and push
git add data/tasks.json
git diff --cached --quiet || {
  git commit -m "Auto: Dispatcher refresh $(date -u +%H:%M)" 2>/dev/null
  git pull --rebase 2>/dev/null  
  git push 2>/dev/null
}
