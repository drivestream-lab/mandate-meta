"""Preflight check 4: Mandate works in Paperclip inside its own run, with reduced permissions.

Reads the token from ~/.mandate/secrets/lab/paperclip-mandate-token and never prints it.
  python3 paperclip_check.py open          wake Mandate's agent, create an issue and ask a two-option question in that run
  python3 paperclip_check.py read <issue>  read the question back: status, answer and who answered
Set PAPERCLIP_URL if Paperclip is not at http://localhost:3100.
"""
import json, os, pathlib, sys
import requests

URL = os.environ.get("PAPERCLIP_URL", "http://localhost:3100").rstrip("/") + "/api"
AGENT = "bb97b5d0-b2ca-40ae-83bf-c0e84ff1187d"
TOKEN = (pathlib.Path.home() / ".mandate/secrets/lab/paperclip-mandate-token").read_text().strip()
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def call(method, path, run=None, **kw):
    h = dict(H)
    if run:
        h["X-Paperclip-Run-Id"] = run
    r = requests.request(method, URL + path, headers=h, timeout=30, **kw)
    try:
        body = r.json()
    except ValueError:
        body = r.text[:300]
    return r.status_code, body


def first(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return None


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "open":
        s, agent = call("GET", f"/agents/{AGENT}")
        print("agent", s, {k: v for k, v in agent.items() if k.startswith("can") or k in ("name", "companyId", "role")} if isinstance(agent, dict) else agent)
        perms = agent.get("permissions") if isinstance(agent, dict) else None
        if perms:
            print("permissions", perms)
        company = first(agent, "companyId")
        s, wake = call("POST", f"/agents/{AGENT}/wakeup", json={"source": "on_demand", "triggerDetail": "manual", "reason": "Preflight check 4"})
        run = first(wake, "id", "runId") or first(first(wake, "run") or {}, "id")
        print("wakeup", s, "run", run, "" if run else wake)
        s, issue = call("POST", f"/companies/{company}/issues", run=run, json={"title": "Preflight check 4", "description": "Mandate creates this issue inside its own run."})
        iid = first(issue, "id")
        print("issue", s, iid, first(issue, "identifier") or "", "" if iid else issue)
        payload = {"version": 1, "title": "Preflight check 4", "questions": [{"id": "preflight-choice", "prompt": "Preflight check 4: choose one option so Mandate can read your answer back.", "selectionMode": "single", "required": True, "options": [{"id": "option-a", "label": "Option A"}, {"id": "option-b", "label": "Option B"}]}]}
        s, q = call("POST", f"/issues/{iid}/interactions", run=run, json={"kind": "ask_user_questions", "continuationPolicy": "none", "payload": payload})
        print("question", s, first(q, "id"), first(q, "status") or "", "" if first(q, "id") else q)
        print(f"\nAnswer it in the Paperclip inbox, then run: python3 {sys.argv[0]} read {iid}")
    elif cmd == "read":
        s, items = call("GET", f"/issues/{sys.argv[2]}/interactions")
        items = items if isinstance(items, list) else first(items, "items", "interactions") or items
        for it in items if isinstance(items, list) else [items]:
            keep = {k: it.get(k) for k in ("id", "kind", "status", "result", "response", "answers", "resolvedAt", "resolvedByUserId", "resolvedByAgentId", "createdByAgentId", "createdByRunId") if isinstance(it, dict) and k in it}
            print(json.dumps(keep, indent=2, default=str))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
