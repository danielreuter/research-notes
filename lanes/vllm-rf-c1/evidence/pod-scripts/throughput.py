"""Per-scheme commit throughput of #101's Commit rows (head and base): the `commit` section of each `commit/runs.jsonl` row.
usage: python3 throughput.py ROW        prints JSON: per tree, per row, run_root / leaves / bytes_bound / spans_* / spans_throughput"""
import json
import sys

ROW = sys.argv[1]
KEYS = ("run_root", "steps", "leaves", "bytes_bound", "tensors", "spans_total_s", "spans_calls", "spans_bytes", "spans_throughput",
        "root_ready_delay_s", "finalize_s")
out = {}
for tag in ("head", "base"):
    p = f"/workspace/cp/sweep-{tag}/{ROW}/commit/runs.jsonl"
    rows = []
    try:
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            c = r.get("commit") or {}
            rows.append({"committer": r.get("committer"), "kind": r.get("kind"), "wall_s": r.get("wall_s"), "row_keys": sorted(r),
                         "weight_registration": c.get("weight_registration") or r.get("weight_registration"), **{k: c.get(k) for k in KEYS}})
    except Exception as e:  # noqa: BLE001
        rows = [{"error": f"{type(e).__name__}: {e}"}]
    out[tag] = rows
print(json.dumps(out, indent=1, default=str))
