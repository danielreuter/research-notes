"""Build packages/verity/tests/ml/fixtures/tc-hopper-wgmma-bf16-2026-09-26/records.json.gz from fetched tc_probe runs.

    python build_fixture.py OUT.json.gz RUN_DIR [RUN_DIR ...]

Per run (a tc_probe --sweep [--chain] --replay-capture run of sm90.wgmma.m64n8k16.bf16, or of sm90.mma.m16n8k16.bf16 with
--also-model hopper_bf16_wgmma_k16:total): the run's capture_sample.json records
(60 per family, one wgmma each), every distinct element of the specials family (tiles_specials.npz: rows 0..15 hold the 16 a
classes, columns the 8 b classes; rows 16..63 repeat them), and 30 elements per chained family (tiles_chain4_<family>.npz,
four back-to-back wgmma, a/b 64 words).  The run's per-family counts come from probe_results.json.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np

CHAIN_PER_FAMILY = 30


def hexwords(ws, width=4) -> str:
    return "".join(f"{int(w):0{width}x}" for w in ws)


def rec(C, A, Bt, D, t, i, j, family, run, steps):
    return {"run": run, "family": family, "steps": steps, "acc": f"{int(C[t, i, j]):08x}", "a": hexwords(A[t, i]),
            "b": hexwords(Bt[t, j]), "d": f"{int(D[t, i, j]):08x}"}


def main() -> None:
    out, runs = Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]
    doc = {"instruction": "sm90.wgmma.m64n8k16.bf16", "ptx": "wgmma.mma_async.sync.aligned.m64n8k16.f32.bf16.bf16",
           "note": "runs of sm90.mma.m16n8k16.bf16 (instruction field) compare the same model as a hypothesis",
           "model": "hopper_bf16_wgmma_k16 (total semantics)", "runs": {}, "records": []}
    for rd in runs:
        pr = json.loads((rd / "probe_results.json").read_text())
        run = rd.name
        ident, sw, ch, cap = pr["identity"], pr["sweep"], pr.get("chain_sweep"), pr["capture_replay"]
        declared = pr["instruction"]["models"][0]["name"]
        doc["runs"][run] = {
            "instruction": pr["instruction"]["id"], "a_source": ident["a_source"], "kernel": ident["kernel"], "device": ident["device"], "driver": ident["driver"],
            "gpu_uuid": ident["gpu_uuid"], "nvcc": ident["nvcc"], "arch": ident["arch"],
            "sass": sorted({m for f in pr["sass"]["tile_kernel_functions"].values() for m in f["mma"]}),
            "sass_count": pr["sass"]["tile_kernel_mma_count"], "seed": sw["seed"], "n_random": sw["n_random"],
            "sweep": {name: {"elements": f["elements"], "mismatches": {m: v["mismatches"] for m, v in f["models"].items()}}
                      for name, f in sw["families"].items()},
            "chain": None if ch is None else {
                "steps": ch["steps"], "seed": ch["seed"], "n_random": ch["n_random"],
                "families": {name: {"elements": f["elements"], "mismatches": {m: v["mismatches"] for m, v in f["models"].items()}}
                             for name, f in ch["families"].items()}},
            "capture_replay": {k: cap[k] for k in ("records", "model", "mismatches", "model_mismatches", "other_positions_nonzero")},
            "declared_model": declared, "failures": pr["failures"],
        }
        for r in json.loads((rd / "capture_sample.json").read_text())["records"]:
            doc["records"].append({"run": run, "family": r["family"], "steps": 1, **{k: r[k] for k in ("acc", "a", "b", "d")}})
        z = np.load(rd / "tiles_specials.npz")
        A, Bt, C, D = z["A"], z["Bt"], z["C"], z["D"]
        seen = set()
        for t in range(A.shape[0]):
            for i in range(16):
                for j in range(8):
                    r = rec(C, A, Bt, D, t, i, j, "specials/all", run, 1)
                    key = (r["acc"], r["a"], r["b"])
                    if key not in seen:
                        seen.add(key)
                        doc["records"].append(r)
        rng = np.random.default_rng(20260926)
        for name in (ch or {"families": {}})["families"]:
            z = np.load(rd / f"tiles_chain4_{name}.npz")
            A, Bt, C, D = z["A"], z["Bt"], z["C"], z["D"]
            n, M, N = D.shape
            for f in sorted(rng.choice(n * M * N, size=min(CHAIN_PER_FAMILY, n * M * N), replace=False).tolist()):
                t, i, j = f // (M * N), (f % (M * N)) // N, f % N
                doc["records"].append(rec(C, A, Bt, D, t, i, j, f"chain4/{name}", run, 4))
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    print(out, len(doc["records"]), "records", {r: v["a_source"] for r, v in doc["runs"].items()})


if __name__ == "__main__":
    main()
