"""Research pod spend ledger (coordinator): every poll adds rate x elapsed for each running research pod (name vy-*, not
vy-control*, not vyv-*) to spend-ledger.json. Window starts 2026-09-25T06:51Z (11:51 PM PT), the start of the $300 research budget.

    python spend-ledger.py [--every 120]      # poll forever
    python spend-ledger.py --report           # print the total and per pod
"""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projects/verity-main-wt/cli/tools/research/src"))
from research.pods import runpod  # noqa: E402

LEDGER = Path(__file__).with_name("spend-ledger.json")
WINDOW_START = "2026-09-25T06:51:00Z"


def research(name: str) -> bool:
    return name.startswith("vy-") and not name.startswith("vy-control")


def load() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"window_start": WINDOW_START, "pods": {}, "last_poll": None}


def poll(doc: dict) -> dict:
    now = time.time()
    last = doc.get("last_poll") or datetime.strptime(WINDOW_START, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    dt = max(0.0, min(now - last, 600.0))          # cap a gap (laptop asleep) at 10 min so a stale gap never inflates spend
    pods = runpod._request("GET", "/pods") or []
    for p in pods:
        name = p.get("name") or ""
        if not research(name) or p.get("desiredStatus") != "RUNNING":
            continue
        rate = float(p.get("costPerHr") or 0.0)
        e = doc["pods"].setdefault(p["id"], {"name": name, "usd": 0.0, "rate": rate, "first_seen": now})
        e["usd"] = round(e["usd"] + rate * dt / 3600.0, 4)
        e["rate"], e["last_seen"] = rate, now
    doc["last_poll"] = now
    doc["total_usd"] = round(sum(e["usd"] for e in doc["pods"].values()), 3)
    doc["running_rate"] = round(sum(e["rate"] for e in doc["pods"].values() if now - e.get("last_seen", 0) < 300), 3)
    LEDGER.write_text(json.dumps(doc, indent=1))
    return doc


if __name__ == "__main__":
    if "--report" in sys.argv:
        d = load()
        print(f"research spend since 11:51 PM PT: ${d.get('total_usd', 0):.2f} of $300; running ${d.get('running_rate', 0):.2f}/h")
        for pid, e in sorted(d["pods"].items(), key=lambda kv: -kv[1]["usd"]):
            print(f"  {e['name']:<40} ${e['usd']:.2f} (${e['rate']}/h)")
        sys.exit(0)
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 120
    while True:
        try:
            poll(load())
        except Exception as e:  # noqa: BLE001
            print(f"{datetime.now(timezone.utc):%H:%MZ} poll failed: {type(e).__name__}: {e}", flush=True)
        time.sleep(every)
