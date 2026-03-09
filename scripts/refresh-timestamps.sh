#!/bin/bash
cd "$(dirname "$0")/.."
python3 -c "
import json, datetime
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
with open('data/tasks.json') as f:
    d = json.load(f)
for a in d['agents']:
    a['updated_at'] = now
d['generated_at'] = now
with open('data/tasks.json','w') as f:
    json.dump(d, f, indent=2)
"
git add data/tasks.json
git commit -m "Auto: Refresh timestamps $(date -u +%H:%M)" 2>/dev/null
git pull --rebase 2>/dev/null
git push 2>/dev/null
