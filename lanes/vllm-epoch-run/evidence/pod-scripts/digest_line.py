"""digest_line.py N EVIDENCE_DIR RUN EPOCH_SHA SPENT GATE [PAIRS CLOUD DRIVER ATTEMPTS]: row N's line in the epoch's digest table (the brief's columns), and its full
digests in the JSON beside it.  The table is `$STORE/internal/lanes/vllm-coordinator/<stamp>-epoch-digests.md` (stamp fixed by the first
row, kept in evidence/digests_path); a row already in the table is replaced, never duplicated."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HEAD = """---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: report · from: vllm-epoch-run (bc-75fd4007) · created: {created} · re: `lane-briefs/vllm-epoch-run.md` "Out"

# Re-baseline epoch: per-row digests (Q_word v1 as the partition of record)

One line per row as it lands. Digests are the first 16 hex; the full values are in `{json}` beside this file. "written" means
`rebaseline write` took the row (`expected/` commit on the lane's branch); "deferred" means it was not written, with the reason.

| row | main sha | step / request / workload Program digests | manifest | run root | partition digest | verdict | run id | $ |
|---|---|---|---|---|---|---|---|---|
"""


def short(x: str | None) -> str:
    return (x or "-")[:16]


def main() -> int:
    n, ev, run, sha, spent, gate = sys.argv[1:7]
    pairs = sys.argv[7] if len(sys.argv) > 7 else "3"
    cloud, driver = (sys.argv[8], sys.argv[9]) if len(sys.argv) > 9 else ("?", "?")
    att = Path(sys.argv[10]) if len(sys.argv) > 10 else None
    refused = sum(1 for ln in att.read_text().splitlines() if "REFUSED" in ln or "fail-fast" in ln) if att and att.exists() else 0
    ev = Path(ev)
    lane = Path(os.environ["RESEARCH_NOTES"]) / "lanes" / "vllm-epoch-run" / "evidence"
    pp = lane / "digests_path"
    if not pp.exists():
        stamp = time.strftime("%Y%m%dT%H%MZ", time.gmtime())
        pp.write_text(str(Path(os.environ["STORE"]) / "internal" / "lanes" / "vllm-coordinator" / f"{stamp}-epoch-digests.md") + "\n")
    md = Path(pp.read_text().strip())
    js = md.with_suffix(".json")
    dg = json.loads((ev / "digests.json").read_text()) if (ev / "digests.json").exists() else {"rows": [{}]}
    r = (dg.get("rows") or [{}])[0]
    progs = r.get("programs") or {}
    cells = []
    for rank in sorted(progs, key=int):
        p = progs[rank]
        reqs = p.get("requests") or {}
        first = next(iter(reqs.values()), None)
        cells.append(("" if len(progs) == 1 else f"r{rank}: ") + f"{short(p.get('step'))} / {len(reqs)} req ({short(first)}{', ...' if len(reqs) > 1 else ''})"
                     f" / {short(p.get('workload'))}")
    parts = r.get("partition_digests") or []
    verdict = r.get("verdict") or "-"
    fate = "written" if gate.startswith("WRITE") else "deferred: " + gate.removeprefix("HOLD ")[:160]
    if pairs == "1" and n != "101":
        fate += " (1 pair, time fallback: n_runs 6 -> 2)"
    line = (f"| #{n} | {sha[:8]} | {'<br>'.join(cells) or '-'} | {short(r.get('manifest_digest'))} | "
            f"{', '.join(short(x) for x in r.get('run_roots') or []) or '-'} | {short(parts[0]) if parts else '-'}"
            f"{f' (+{len(parts) - 1})' if len(parts) > 1 else ''} | {verdict}, {fate} | {run} ({cloud.lower()}, driver {driver}"
            f"{f'; {refused} offer(s) refused' if refused else ''}) | {spent} |")
    text = md.read_text() if md.exists() else HEAD.format(created=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), json=js.name)
    rows = [ln for ln in text.splitlines() if not ln.startswith(f"| #{n} |")]
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("\n".join(rows + [line]) + "\n")
    full = json.loads(js.read_text()) if js.exists() else {"schema": "vllm-epoch-run/epoch-digests/v1", "rows": {}}
    full["rows"][n] = {**r, "main_sha": sha, "run": run, "spent_usd": float(spent), "gate": gate, "pairs": int(pairs), "cloud": cloud, "driver": driver, "offers_refused": refused}
    js.write_text(json.dumps(full, indent=1) + "\n")
    print(line)
    print(f"table: {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
