"""Per key count, the captured #101 attention heads as a set of their own (input_sets.subset: same name and relation,
provenance subset_of), registered as input-set/v1 with the parent set as a ref."""
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

from verity_numerical.bench.input_sets import InputSet, subset

PARENT_ART = "art:6312cb50d48f24a50697068ec3b6c597bf5369d66fd37def0ab45b78a82b1a1a"
src = Path.home() / ".research/store/trees" / PARENT_ART[4:]
root = Path(sys.argv[1])
ix = json.loads((src / "index.json").read_text())
cols, rows = ix["columns"], ix["rows"]
runs = OrderedDict()
for i, r in enumerate(rows):
    T = r[cols.index("sub")]["T"]
    lo, hi = runs.get(T, (i, i))
    if hi != i:
        raise SystemExit(f"T={T} instances are not contiguous")
    runs[T] = (lo, i + 1)
out = {}
for T, (lo, hi) in sorted(runs.items()):
    d = subset(src, root / f"t{T}", lo, hi)
    s = InputSet.open(d)
    meta = dict(s.meta(), key_count=T, subset_of={"art": PARENT_ART, "range": [lo, hi]})
    mf = root / f"t{T}.meta.json"
    mf.write_text(json.dumps(meta, default=str))
    r = subprocess.run(["research", "data", "put", "--kind", "input-set/v1", "--tree", str(d), "--meta", f"@{mf}", "--ref",
                        f"subset_of={PARENT_ART}", "--preserve", "--json"], capture_output=True, text=True)
    art = json.loads(r.stdout)["id"] if r.returncode == 0 else None
    out[T] = {"art": art, "range": [lo, hi], "path": str(d), "content_digest": s.content_digest, "rc": r.returncode,
              "err": r.stderr[-300:] if r.returncode else None}
    print(T, out[T]["art"], out[T]["rc"], flush=True)
(root / "subsets.json").write_text(json.dumps(out, indent=1))
