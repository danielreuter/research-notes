"""verify-night: an independent cross-check of the 15 instance-equiv/v1 files, not using instance_equiv.py's decoding.

For each file: the candidate relation (from the file name) and the frozen base relation (the target's registered relation whose
relchain.instances_ref at n = 4096 equals tables.FROZEN_INSTANCES[target], found here by my own scan); both sides drawn with
relchain.instances(rel, 4096) WITHOUT a cache (so a fold never reuses its base's arrays); then per VU:
  a == a, b == b (operand words), candidate accs == base accs[fold_c - 1 :: fold_c / fold_b] (every recorded public
  accumulator, not only the final one), y_final == y_final;
and my own sha256 of x, W, y in the §5 canonical form compared with the file's frozen_sha256 / candidate_sha256.
Also: file.frozen == FROZEN_INSTANCES[target] field for field; file.candidate == relchain.instances_ref(cand, 4096).

    python 05-equiv-independent.py DIR/*.json/*.json > out.json
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from verity_numerical.bench.tables import FROZEN_INSTANCES

N = 4096
PROCS = int(os.environ.get("VY_CPU_THREADS", os.cpu_count() or 1))
_memo = {}


def load(rel):
    if rel.name not in _memo:
        t0 = time.time()
        _memo[rel.name] = relchain.instances(rel, N, procs=PROCS)
        print(f"# drew {rel.name}: {len(_memo[rel.name])} VUs in {time.time() - t0:.1f}s", file=sys.stderr, flush=True)
    return _memo[rel.name]


def sha(rows, dt):
    return hashlib.sha256(np.asarray(rows, dtype=np.int64).astype(np.dtype(dt).newbyteorder("<")).tobytes()).hexdigest()


def keyref(r):
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in r.items() if k in ("dataset", "tier", "range", "manifest_sha256")}


def main(paths):
    out = []
    for p in paths:
        doc = json.load(open(p))
        name = os.path.basename(p).removeprefix("instance-equiv-").removesuffix(f"-{N}.json")
        cand = RELATIONS[name]
        target = doc["target"]
        want = FROZEN_INSTANCES[target]
        bases = [r for r in RELATIONS.values() if r.target.name == target and keyref(relchain.instances_ref(r, N)) == keyref(want)]
        base = min(bases, key=lambda r: (r.fold, len(r.name)))
        res = {"file": p, "relation": name, "target": target, "base": base.name, "base_candidates": sorted(r.name for r in bases),
               "fold": [base.fold, cand.fold], "word_dtype": [base.word_dtype, cand.word_dtype]}
        res["frozen_ref_ok"] = keyref(doc["frozen"]) == keyref(want)
        res["candidate_ref_ok"] = doc["candidate"] == relchain.instances_ref(cand, N)
        B, C = load(base), load(cand)
        step = cand.fold // base.fold if cand.fold % base.fold == 0 else None
        bad = {"a": 0, "b": 0, "accs": 0, "y": 0}
        for (ba, bb, bacc, by), (ca, cb, cacc, cy) in zip(B, C):
            bad["a"] += list(ba) != list(ca)
            bad["b"] += list(bb) != list(cb)
            bad["accs"] += step is None or [int(x) for x in bacc[step - 1::step]] != [int(x) for x in cacc]
            bad["y"] += int(by) != int(cy)
        res["mismatched_vus"] = bad
        res["n"] = [len(B), len(C)]
        wd = cand.word_dtype
        mine = {"x": (sha([u[0] for u in B], wd), sha([u[0] for u in C], wd)), "W": (sha([u[1] for u in B], wd), sha([u[1] for u in C], wd)),
                "y": (sha([int(u[3]) for u in B], "<u4"), sha([int(u[3]) for u in C], "<u4"))}
        res["digests_match_file"] = {k: [mine[k][0] == doc["arrays"][k]["frozen_sha256"], mine[k][1] == doc["arrays"][k]["candidate_sha256"]] for k in mine}
        res["equal_mine"] = all(v == 0 for v in bad.values()) and all(f == c for f, c in mine.values()) and len(B) == len(C) == N
        res["ok"] = bool(res["equal_mine"] and res["frozen_ref_ok"] and res["candidate_ref_ok"] and doc["equal"] is True
                         and all(all(v) for v in res["digests_match_file"].values()))
        print(f"# {name}: ok={res['ok']} base={base.name} mism={bad} digests={res['digests_match_file']}", file=sys.stderr, flush=True)
        out.append(res)
    print(json.dumps(out, indent=1))
    return 0 if all(r["ok"] for r in out) else 1


if __name__ == "__main__":
    sys.exit(main(sorted(sys.argv[1:]) or sorted(glob.glob("/workspace/verify-night/equiv/*.json/*.json"))))
