#!/usr/bin/env python3
import json, os, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

RAW_URL = "https://raw.githubusercontent.com/codenameagentd-cloud/mission-control-dashboard/main/data/activities.json"
WEBHOOK_PATH = os.path.expanduser("~/.config/mission-control/webhook_url")
STATE_PATH = os.path.expanduser("~/.config/mission-control/last_ts")


def read_webhook():
    with open(WEBHOOK_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def read_last_ts():
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip() or None


def write_last_ts(ts):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write(ts)


def fetch_events():
    req = Request(RAW_URL, headers={"User-Agent": "mission-control-notifier"})
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("events", [])


def post_webhook(url, content):
    payload = json.dumps({"content": content}).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as resp:
        resp.read()


def main():
    webhook = read_webhook()
    last_ts = read_last_ts()
    events = fetch_events()

    filtered = [e for e in events if e.get("type") in ("completed", "error")]

    def parse_ts(t):
        try:
            return datetime.fromisoformat(t.replace("Z", "+00:00"))
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    filtered.sort(key=lambda e: parse_ts(e.get("ts", "")))

    new_events = []
    for e in filtered:
        ts = e.get("ts")
        if not ts:
            continue
        if last_ts and parse_ts(ts) <= parse_ts(last_ts):
            continue
        new_events.append(e)

    if not new_events:
        return

    for e in new_events:
        agent = e.get("agent_id", "unknown")
        summary = e.get("summary", "")
        etype = e.get("type", "")
        link = e.get("link")
        msg = f"✅ [{etype}] {agent}: {summary} ({e.get('ts')})"
        if link:
            msg += f"\n{link}"
        post_webhook(webhook, msg)
        write_last_ts(e.get("ts"))
        time.sleep(0.3)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
