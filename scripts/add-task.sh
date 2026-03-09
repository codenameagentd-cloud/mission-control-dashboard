#!/bin/bash
# Usage: add-task.sh <agent_id> <task_title> [priority]
cd "$(dirname "$0")/.."
AGENT="$1"
TITLE="$2"
PRIORITY="${3:-MEDIUM}"

python3 - "$AGENT" "$TITLE" "$PRIORITY" << 'PYEOF'
import json, sys, datetime, uuid

agent_id = sys.argv[1]
title = sys.argv[2]  
priority = sys.argv[3]

with open('data/tasks.json') as f:
    data = json.load(f)

now = datetime.datetime.now(datetime.timezone.utc).isoformat()

for a in data['agents']:
    if a['id'] == agent_id:
        if 'task_queue' not in a:
            a['task_queue'] = []
        task = {
            'id': f't-{uuid.uuid4().hex[:8]}',
            'title': title,
            'progress': 0,
            'priority': priority,
            'active': len([t for t in a['task_queue'] if t.get('active')]) == 0
        }
        a['task_queue'].append(task)
        a['current_task'] = title if task['active'] else a.get('current_task', '')
        a['status'] = 'busy'
        a['updated_at'] = now
        print(f"Added task '{title}' to {agent_id} (active={task['active']})")
        break
else:
    print(f"Agent {agent_id} not found")
    sys.exit(1)

data['generated_at'] = now
with open('data/tasks.json', 'w') as f:
    json.dump(data, f, indent=2)
PYEOF

git add data/tasks.json
git commit -m "Task: $TITLE → $AGENT" 2>/dev/null
git pull --rebase 2>/dev/null
git push 2>/dev/null
