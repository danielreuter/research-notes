"""Shape analysis over the census pickles (one <row>.pkl per row): distributions, outliers, candidate shapes, mixes."""
import __main__
import glob
import json
import pickle
import sys
import time
from collections import Counter, defaultdict

import numpy as np

sys.path[:0] = ["/workspace/packages/verity/src", "/workspace/backends/numerical/python", "/workspace/backends/flock/python",
                "/workspace/integrations/vllm"]
from verity_flock import unit_shapes as US  # noqa: E402

__main__.UnitShape = US.UnitShape
OUT = sys.argv[1]
rows = {p.split("/")[-1][:-4]: pickle.loads(open(p, "rb").read()) for p in sorted(glob.glob(f"{OUT}/*.pkl"))}


def lg(x):
    return int(x).bit_length() - 1


def family(u):
    s = (u.scope or u.head or "?").split("{")[0]
    return f"{s} / {u.kind} / {u.head}"


res = {"programs": {}, "shapes": {}, "mixes": {}}
for key, classes in rows.items():
    fam = defaultdict(lambda: {"units": 0, "rows": 0.0, "z": 0.0, "d": 0.0, "R": set(), "Zb": set(), "Db": set(), "max_rows": 0,
                               "max_z": 0, "max_d": 0, "lookups": 0, "est": set()})
    hist = {"R": Counter(), "Z": Counter(), "D": Counter(), "Rw": Counter()}
    for u, cnt, tp in classes:
        f = fam[family(u)]
        f["units"] += cnt
        f["rows"] += cnt * u.rows
        f["z"] += cnt * u.z
        f["d"] += cnt * u.d
        f["R"].add(lg(u.R))
        f["Zb"].add(lg(US.pow2(max(u.z, 1))))
        f["Db"].add(lg(US.pow2(max(u.d, 1))))
        f["max_rows"] = max(f["max_rows"], u.rows)
        f["max_z"] = max(f["max_z"], u.z)
        f["max_d"] = max(f["max_d"], u.d)
        f["lookups"] = max(f["lookups"], len(u.lookups))
        f["est"] |= set(u.estimated)
        hist["R"][lg(u.R)] += cnt
        hist["Z"][lg(US.pow2(max(u.z, 1)))] += cnt
        hist["D"][lg(US.pow2(max(u.d, 1)))] += cnt
        hist["Rw"][lg(u.R)] += cnt * u.rows
    res["programs"][key] = {"families": {k: {**v, "R": sorted(v["R"]), "Zb": sorted(v["Zb"]), "Db": sorted(v["Db"]), "est": sorted(v["est"])}
                                         for k, v in fam.items()},
                            "hist": {k: dict(v) for k, v in hist.items()},
                            "n": sum(c for _u, c, _t in classes), "rows": sum(c * u.rows for u, c, _t in classes),
                            "z": sum(c * u.z for u, c, _t in classes), "d": sum(c * u.d for u, c, _t in classes)}

MODE = sys.argv[2] if len(sys.argv) > 2 else "main"
if MODE == "main":
    cands = [(1 << k, 1 << (k + 5), 1 << (k - 8)) for k in range(14, 24)]
elif MODE == "z":
    cands = [(1 << k, 1 << (k + zk), 1 << (k - 8)) for k in range(15, 23) for zk in (4, 6)]
else:
    cands = [(1 << k, 1 << (k + 5), 1 << (k + dk)) for k in range(15, 23) for dk in (-9, -7, -6)]
cache: dict = {}
t = time.time()
for S in cands:
    res["shapes"][f"{lg(S[0])},{lg(S[1])},{lg(S[2])}"] = {key: US.assess(classes, S, cache) for key, classes in rows.items()}
    print(S, f"{time.time() - t:.0f}s", file=sys.stderr, flush=True)


def assess_mix(classes, shapes, cache):
    """Each unit in the smallest shape it fits, else split to the largest: per shape n_i, and the totals."""
    shapes = sorted(shapes)
    big = shapes[-1]
    n = Counter()
    used = np.zeros(3)
    extra = 0
    for u, cnt, *_ in classes:
        S = next((S for S in shapes if u.R <= S[0] and u.z <= S[1] and u.d <= S[2]), None)
        if S is not None:
            n[S] += cnt
            used += cnt * np.array([u.rows, u.z, u.d], float)
            continue
        k = (id(u), big)
        if k not in cache:
            cache[k] = US.pack_best(u.seq, *big) if u.seq else {"pieces": 1, "extra": 0, "oversize": 1, "each": [{"rows": u.rows, "z": u.z, "d": u.d}]}
        p = cache[k]
        for e in p["each"]:
            S2 = next(S for S in shapes if US.pow2_slot(e["rows"]) <= S[0] and e["z"] <= S[1] and e["d"] <= S[2]) if all(
                US.pow2_slot(e["rows"]) <= big[0] and e["z"] <= big[1] and e["d"] <= big[2] for e in [e]) else big
            n[S2] += cnt
        used += cnt * np.array([sum(e["rows"] for e in p["each"]), sum(e["z"] for e in p["each"]), sum(e["d"] for e in p["each"])], float)
        extra += cnt * p["extra"]
    padded = np.array([sum(n[S] * S[i] for S in n) for i in range(3)], float)
    return {"n": {f"{lg(S[0])},{lg(S[1])},{lg(S[2])}": n[S] for S in shapes}, "n_total": sum(n.values()), "extra_commitments": extra,
            "waste_rows": 1 - used[0] / padded[0], "waste_z": 1 - used[1] / padded[1], "waste_d": 1 - used[2] / padded[2],
            "padded_rows": padded[0], "used_rows": used[0]}


def S(k, zk=5, dk=-8):
    return (1 << k, 1 << (k + zk), 1 << (k + dk))


mixes = {}
if MODE == "main":
    for a in range(12, 18):
        for b in range(a + 2, 24):
            mixes[f"{a}|{b}"] = [S(a), S(b)]
    for a in range(12, 16):
        for b in range(a + 2, 20):
            for c in range(b + 2, 24):
                mixes[f"{a}|{b}|{c}"] = [S(a), S(b), S(c)]
t = time.time()
for name, shapes in mixes.items():
    res["mixes"][name] = {key: assess_mix(classes, shapes, cache) for key, classes in rows.items()}
print("mixes", f"{time.time() - t:.0f}s", file=sys.stderr, flush=True)
json.dump(res, open(f"{OUT}/analysis-{MODE}.json", "w"), default=float)
