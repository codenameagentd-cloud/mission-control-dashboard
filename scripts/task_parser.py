#!/usr/bin/env python3
"""Parse [task] @Agent messages and write to tasks.json.

Usage: 
  python3 task_parser.py "<message text>"
  python3 task_parser.py "<message text>" --priority HIGH
"""
import json, re, datetime, uuid, sys, os

AGENTS_MAP = {
    '1478284015269187654': 'jony',
    '1478286708192706641': 'lisa',
    '1478287578628227184': 'jarvis',
    '1478288552272855222': 'naomi',
    '1478289134190727168': 'jennie',
}
NAME_MAP = {n: n for n in ['jony','lisa','jarvis','naomi','jennie']}
TASKS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks.json')

def parse_task_message(text):
    m = re.match(r'\[task\]\s*(?:<@!?(\d+)>|@(\w+))\s+(.+)', text, re.IGNORECASE)
    if not m: return None
    did, name, title = m.group(1), m.group(2), m.group(3).strip()
    agent = AGENTS_MAP.get(did) if did else NAME_MAP.get((name or '').lower())
    return (agent, title) if agent and title else None

def add_task(agent_id, title, priority='MEDIUM'):
    with open(TASKS_PATH) as f: data = json.load(f)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for a in data['agents']:
        if a['id'] == agent_id:
            a.setdefault('task_queue', [])
            active = not any(t.get('active') for t in a['task_queue'])
            task = {'id': f't-{uuid.uuid4().hex[:8]}', 'title': title, 'progress': 0, 'priority': priority, 'active': active}
            a['task_queue'].append(task)
            if active: a['current_task'] = title; a['status'] = 'busy'
            a['updated_at'] = now
            data['generated_at'] = now
            with open(TASKS_PATH, 'w') as f: json.dump(data, f, indent=2)
            print(json.dumps({'ok': True, 'agent': agent_id, 'task': task}))
            return
    print(json.dumps({'ok': False, 'error': f'Agent {agent_id} not found'}))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: task_parser.py "<message>"'); sys.exit(1)
    msg = sys.argv[1]
    priority = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--priority' else 'MEDIUM'
    result = parse_task_message(msg)
    if result:
        add_task(result[0], result[1], priority)
    else:
        print(json.dumps({'ok': False, 'error': 'No [task] pattern found'}))
