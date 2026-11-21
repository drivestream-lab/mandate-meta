"""Preflight checks 1 and 2: the required check gates the merge; a signoff is readable and the App can write it.

Reads secret file paths only, never prints a secret. Usage:
  python preflight.py status   <repo> <sha> <success|failure>   post mandate/gate-decision as the test App
  python preflight.py signoff  <repo> <pr>                       read label, latest Approve body and ready state on the head
  python preflight.py app-sign <repo> <pr> <label>              App applies label, Approve with an attestation body, marks ready
  python preflight.py merge    <repo> <pr>                       try to merge as the App with sha pinned to the head
  python preflight.py open     <repo> <branch> <title>            the App opens a draft PR from <branch> into develop
"""
import json, pathlib, sys, time
import jwt, requests

SECRETS = pathlib.Path.home() / ".mandate" / "secrets" / "test"
API = "https://api.github.com"
OWNER = "drivestream-lab"
CHECK = "mandate/gate-decision"


def _read(name: str) -> str:
    return (SECRETS / name).read_text().strip()


def token() -> str:
    key = next(SECRETS.glob("*.private-key.pem")).read_text()
    now = int(time.time())
    app_jwt = jwt.encode({"iat": now - 60, "exp": now + 540, "iss": _read("github-app-id")}, key, algorithm="RS256")
    r = requests.post(f"{API}/app/installations/{_read('github-app-installation-id')}/access_tokens",
                      headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"}, timeout=30)
    r.raise_for_status()
    return r.json()["token"]


def h(t: str) -> dict:
    return {"Authorization": f"Bearer {t}", "Accept": "application/vnd.github+json"}


def pr(t: str, repo: str, n: str) -> dict:
    r = requests.get(f"{API}/repos/{OWNER}/{repo}/pulls/{n}", headers=h(t), timeout=30); r.raise_for_status(); return r.json()


def main() -> None:
    cmd, repo = sys.argv[1], sys.argv[2]
    t = token()
    if cmd == "status":
        sha, state = sys.argv[3], sys.argv[4]
        r = requests.post(f"{API}/repos/{OWNER}/{repo}/statuses/{sha}", headers=h(t), timeout=30,
                          json={"state": state, "context": CHECK, "description": f"preflight {state}"})
        print(r.status_code, r.json().get("state"))
    elif cmd == "signoff":
        p = pr(t, repo, sys.argv[3]); head = p["head"]["sha"]
        reviews = requests.get(f"{API}/repos/{OWNER}/{repo}/pulls/{sys.argv[3]}/reviews", headers=h(t), timeout=30).json()
        approves = [x for x in reviews if x["state"] == "APPROVED" and x["commit_id"] == head]
        print(json.dumps({"head": head, "labels": [l["name"] for l in p["labels"]], "ready": not p["draft"],
                          "approve_on_head": [{"by": a["user"]["login"], "body": a["body"]} for a in approves]}, indent=2))
    elif cmd == "app-sign":
        n, label = sys.argv[3], sys.argv[4]; p = pr(t, repo, n); head = p["head"]["sha"]
        r1 = requests.post(f"{API}/repos/{OWNER}/{repo}/issues/{n}/labels", headers=h(t), json={"labels": [label]}, timeout=30)
        body = f"attestation:\n  initiative: INIT-PREFLIGHT\n  head: {head}\n  gate: {label}\n"
        r2 = requests.post(f"{API}/repos/{OWNER}/{repo}/pulls/{n}/reviews", headers=h(t), timeout=30,
                           json={"commit_id": head, "event": "APPROVE", "body": body})
        q = "mutation($id:ID!){markPullRequestReadyForReview(input:{pullRequestId:$id}){pullRequest{isDraft}}}"
        r3 = requests.post(f"{API}/graphql", headers=h(t), json={"query": q, "variables": {"id": p["node_id"]}}, timeout=30)
        print("label", r1.status_code, "approve", r2.status_code, "ready", r3.status_code, r3.json().get("errors"))
    elif cmd == "merge":
        p = pr(t, repo, sys.argv[3])
        r = requests.put(f"{API}/repos/{OWNER}/{repo}/pulls/{sys.argv[3]}/merge", headers=h(t), timeout=30,
                         json={"sha": p["head"]["sha"], "merge_method": "merge"})
        print(r.status_code, r.json().get("message"))
    elif cmd == "open":
        r = requests.post(f"{API}/repos/{OWNER}/{repo}/pulls", headers=h(t), timeout=30,
                          json={"head": sys.argv[3], "base": "develop", "title": sys.argv[4], "draft": True})
        print(r.status_code, r.json().get("html_url"), r.json().get("message"))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
