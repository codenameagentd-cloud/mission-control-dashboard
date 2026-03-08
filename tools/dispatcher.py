#!/usr/bin/env python3
import json, os, time
from datetime import datetime
from urllib.request import Request, urlopen

RAW_TASKS_URL = "https://raw.githubusercontent.com/codenameagentd-cloud/mission-control-dashboard/main/data/tasks.json"
RAW_ACT_URL = "https://raw.githubusercontent.com/codenameagentd-cloud/mission-control-dashboard/main/data/activities.json"
STATE_PATH = os.path.expanduser("~/.config/mission-control/dispatcher_state.json")

AGENT_ID = os.environ.get("AGENT_ID", "")
if not AGENT_ID:
    # set per-agent env in cron
    AGENT_ID = "unknown"


def load_json(url):
    req = Request(url, headers={"User-Agent": "mission-control-dispatcher"})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def append_activity(event):
    # NOTE: write-back is not implemented here (needs write token / gh CLI).
    # This is a placeholder hook for agent-side logging.
    pass


def main():
    tasks = load_json(RAW_TASKS_URL)
    agents = tasks.get("agents", [])
    agent = next((a for a in agents if a.get("id") == AGENT_ID), None)
    if not agent:
        return

    state = load_state()
    prev = state.get(AGENT_ID, {})

    # support task_queue (with active flag) or tasks+active_task_id
    task_queue = agent.get("task_queue")
    if task_queue:
        active = next((t.get("id") for t in task_queue if t.get("active") is True), None)
        priorities = [(t.get("id"), t.get("priority")) for t in task_queue]
    else:
        active = agent.get("active_task_id")
        priorities = [(t.get("id"), t.get("priority")) for t in agent.get("tasks", [])]
    priorities_sorted = sorted([p for p in priorities if p[0]], key=lambda x: x[1] or 0)

    changed = False
    if active and active != prev.get("active_task_id"):
        # TODO: switch task execution
        changed = True
        prev["active_task_id"] = active
        # append_activity({"type":"task_activated", ...})

    if priorities_sorted != prev.get("priorities"):
        changed = True
        prev["priorities"] = priorities_sorted
        # append_activity({"type":"task_reordered", ...})

    if changed:
        state[AGENT_ID] = prev
        save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # silent fail for cron
        pass
