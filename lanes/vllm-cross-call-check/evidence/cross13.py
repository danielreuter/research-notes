"""cross13.py ROWS_DIR OUT_DIR [ROW ...]: query.cross_call (PR #98) over every request Program of each fetched row (all instances.json.gz
under ROWS_DIR/<row>, both ranks of a TP row), one JSON per row: per Program the recompute classes, Calls and gates."""
import glob
import json
import sys
import time
from pathlib import Path

from verity_vllm.query import cross_call as X

rows_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
only = set(sys.argv[3:])
out.mkdir(parents=True, exist_ok=True)
memo: dict = {}
for d in sorted(p for p in rows_dir.iterdir() if p.is_dir()):
    if (only and d.name not in only) or (out / f"{d.name}.json").exists():
        continue
    paths = sorted(p for p in glob.glob(f"{d}/**/instances.json.gz", recursive=True) if "/build_step/" not in p)
    if not paths:
        continue
    t = time.time()
    per = {}
    for p in paths:
        r = X.check_program(p, strict=False, memo=memo)
        per[str(Path(p).relative_to(d))] = r
        print(f"  #{d.name} {Path(p).parent.name}: {r['calls']} calls, {len(r['recomputes'])} class(es), {r['recomputed_gates']} gates, "
              f"refined {r['refined']}, unrefined {r['unrefined']} {time.time() - t:.0f}s", flush=True)
    (out / f"{d.name}.json").write_text(json.dumps({"check": X.CHECK_ID, "row": d.name, "programs": per}, indent=1, default=str) + "\n")
    tot = sum(r["recomputed_gates"] for r in per.values())
    print(f"#{d.name}: {len(paths)} Program(s), {sum(len(r['recomputes']) for r in per.values())} class(es), {tot} gates computed again "
          f"{time.time() - t:.0f}s", flush=True)
print("CROSS-DONE")
