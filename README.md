# Mission Control Dashboard — Data Contract (Draft)

## Repo layout
```
/data/tasks.json
/data/activities.json
/schema/tasks.schema.json
/schema/activities.schema.json
README.md
```

## tasks.json (current state)
- Purpose: one snapshot of all agents.
- Required fields per agent: `id`, `name`, `status`, `current_task`, `progress`, `updated_at`.
- `status` enum: `online | busy | idle | offline`.
- `progress`: 0–100 (integer).

Example:
```
{
  "generated_at": "2026-03-08T07:00:00Z",
  "agents": [
    {
      "id": "naomi",
      "name": "Naomi",
      "status": "busy",
      "current_task": "需求規格撰寫",
      "progress": 80,
      "updated_at": "2026-03-08T06:56:00Z",
      "links": ["https://github.com/.../issues/1"]
    }
  ]
}
```

## activities.json (event stream)
- Purpose: append-only log of activities.
- Required fields: `ts`, `agent_id`, `type`, `summary`.
- `type` enum: `started | updated | completed | blocked | note`.
- Optional: `task_id`, `link`.

Example:
```
{
  "generated_at": "2026-03-08T07:00:00Z",
  "events": [
    {
      "ts": "2026-03-08T06:56:00Z",
      "agent_id": "naomi",
      "type": "completed",
      "summary": "需求規格 v1",
      "link": "https://github.com/.../pull/3"
    }
  ]
}
```

## Logging flow (agent update)
1. `git pull --rebase`
2. Update `/data/tasks.json` (current snapshot)
3. Append event to `/data/activities.json`
4. `git add` → `git commit` → `git push`

## Suggested retention
- Keep only latest 50 events for MVP (schema allows up to 100).
- Frontend can display latest 10.

## Platform-agnostic updates
- All agent updates (Discord/Telegram/other) must write to `data/tasks.json` and `data/activities.json` so the dashboard stays in sync.
