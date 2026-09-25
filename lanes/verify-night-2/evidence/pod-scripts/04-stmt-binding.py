"""verify-night-2 (from verify-night 08-stmt-binding.py): do the dumped statements of a result prove the FROZEN instance set's numbers?

reverify checks each proof against its own statement; this checks the statements against the frozen set. For each result:
fetch its run-files tree (manifest + statements only), and for every sub-batch statement (VUs [lo, hi) per the dump manifest)
compare the chain-end public words (y16 at the chain ends) with y_public(final accumulator) of the frozen set's VUs lo..hi-1,
drawn by the target's frozen relation (instance_equiv.frozen_relation); when the statement carries operand words (a, b with
K columns), compare those with the frozen x / W rows too.

    python 08-stmt-binding.py ART...      (AWS_* read credential in the environment)
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.serialize import read_statement
from research.store.local import LocalStore
from verity_numerical.bench.instance_equiv import frozen_relation

N_FROZEN = 4096
# VN2_N > 4096 (a sweep point past the frozen tier): the statements are compared with MY tree's relchain.instances(rel, N)
# (synthetic recipe continued, or frozen ids recycled i mod 4096), whose first 4096 VUs must equal the frozen set
N = int(os.environ.get("VN2_N", N_FROZEN))
PROCS = int(os.environ.get("VY_CPU_THREADS", os.cpu_count() or 1))
_sets = {}
_own = {}


def own_set(rel, target):
    """(VUs of relchain.instances(rel, N), frozen-prefix report) for N > 4096."""
    if rel.name not in _own:
        vus = relchain.instances(rel, N, procs=PROCS)
        _, fz = frozen_set(target)
        bad = [i for i in range(N_FROZEN) if not (np.array_equal(np.asarray(vus[i][0]).reshape(-1), np.asarray(fz[i][0]).reshape(-1))
                                                  and np.array_equal(np.asarray(vus[i][1]).reshape(-1), np.asarray(fz[i][1]).reshape(-1))
                                                  and rel.y_public(int(vus[i][3])) == frozen_set(target)[0].y_public(int(fz[i][3])))]
        _own[rel.name] = (vus, {"n": N, "set": f"relchain.instances({rel.name}, {N})", "digest": relchain.instances_digest(rel, N),
                                "frozen_prefix_vus": N_FROZEN, "frozen_prefix_mismatched": len(bad)})
    return _own[rel.name]


class _FP4:
    """fp4/chain.py's relation (not in relations.RELATIONS): its instances carry the frozen NVFP4 ref at 4096 VUs."""
    name = "fp4-nvf4"

    @staticmethod
    def y_public(w):
        return int(w)


def frozen_set(target):
    if target not in _sets:
        if target == "fp4-nvf4":
            from backends.direct.ligero.fp4.chain import instances_fp4
            _sets[target] = (_FP4, [(np.asarray(A).reshape(-1), np.asarray(B).reshape(-1), accs, y) for A, B, accs, y in instances_fp4(N)])
        else:
            base, _ = frozen_relation(target, N_FROZEN)
            _sets[target] = (base, relchain.instances(base, N_FROZEN, procs=PROCS))
    return _sets[target]


def check(st, art):
    m = st.get_manifest(art)
    tree = (m.refs or {}).get("run_files")
    out = {"result": art, "run_files": tree}
    if not tree:
        return {**out, "status": "NO-DUMPS"}
    with tempfile.TemporaryDirectory(dir="/workspace/verify-night-2") as td:
        d = st.fetch(tree, Path(td) / "t", paths=["*manifest.json", "*.stmt"])
        # exactly the manifest reverify verifies: proofs/manifest.json, else dumps/manifest.json
        mans = [Path(d) / n / "manifest.json" for n in ("proofs", "dumps") if (Path(d) / n / "manifest.json").is_file()]
        if not mans:
            raise FileNotFoundError(f"{tree}: no proofs/ or dumps/ manifest.json")
        man = json.loads(mans[0].read_text())
        pdir = mans[0].parent
        rel_name = man["relation"]["name"] if isinstance(man.get("relation"), dict) else man.get("relation")
        if str(rel_name).startswith("fp4-nvf4"):
            rel, tname = _FP4, "fp4-nvf4"
        else:
            rel = RELATIONS[str(rel_name).split("+")[0]]
            tname = rel.target.name
        base, vus = frozen_set(tname)
        out.update({"relation": rel_name, "target": tname, "frozen_relation": base.name})
        if N > N_FROZEN:
            if rel is _FP4:
                raise ValueError("fp4-nvf4 past the frozen tier: not handled")
            vus, own = own_set(rel, tname)
            out["beyond_frozen"] = own
        n_stmt = n_vus = y_bad = op_checked = op_bad = 0
        covered = set()
        problems = []
        for f in man.get("files", []):
            if not f.get("stmt"):
                continue
            lo, hi = f["vus"]
            s = read_statement((pdir / f["stmt"]).read_bytes())
            n_stmt += 1
            if s.n_vus != hi - lo:
                problems.append(f"{f['stmt']}: n_vus {s.n_vus} != {hi - lo}")
                continue
            ends = np.arange(s.n_vus) * s.steps + s.steps - 1
            y_st = np.asarray(s.y16, dtype=np.int64)[ends]
            y_fz = np.asarray([rel.y_public(int(vus[i][3])) for i in range(lo, hi)], dtype=np.int64)
            bad = int((y_st != y_fz).sum())
            y_bad += bad
            n_vus += s.n_vus
            covered.update(range(lo, hi))
            a, b = np.asarray(s.a), np.asarray(s.b)
            if s.hash_auth is None and s.shared is None and a.ndim == 2 and a.shape[0] >= s.n_vus * s.steps and a.size:
                # rows are (VU, step) units of k words each: rebuild the VU's K words from its steps
                k = a.shape[1]
                xa = a[: s.n_vus * s.steps].reshape(s.n_vus, s.steps * k)
                xb = b[: s.n_vus * s.steps].reshape(s.n_vus, s.steps * k)
                fx = np.asarray([vus[i][0] for i in range(lo, hi)], dtype=np.int64)
                fw = np.asarray([vus[i][1] for i in range(lo, hi)], dtype=np.int64)
                if xa.shape == fx.shape:
                    op_checked += s.n_vus
                    op_bad += int(((xa != fx).any(1) | (xb != fw).any(1)).sum())
                else:
                    problems.append(f"{f['stmt']}: operand table {a.shape} not comparable with ({s.n_vus}, {fx.shape[1]})")
            if bad and len(problems) < 5:
                problems.append(f"{f['stmt']} VUs [{lo},{hi}): {bad} chain-end words differ from the frozen set")
        reps = sorted({f["rep"] for f in man.get("files", []) if f.get("stmt")})
        out.update({"statements": n_stmt, "reps": reps, "vus_checked": n_vus, "vus_covered": len(covered), "y_mismatched": y_bad,
                    "operand_vus_checked": op_checked, "operand_mismatched": op_bad, "problems": problems})
        prefix_ok = (out.get("beyond_frozen") or {}).get("frozen_prefix_mismatched", 0) == 0
        out["status"] = "BOUND" if (not problems and y_bad == 0 and op_bad == 0 and len(covered) == N and prefix_ok) else "NOT-BOUND"
    return out


def main(arts):
    st = LocalStore()
    res = []
    for a in arts:
        try:
            r = check(st, a)
        except Exception as e:  # noqa: BLE001
            r = {"result": a, "status": "ERROR", "why": f"{type(e).__name__}: {e}"}
        print(f"# {a[:16]} {r.get('status')} {r.get('relation')} stmts={r.get('statements')} vus={r.get('vus_covered')} "
              f"y_bad={r.get('y_mismatched')} ops={r.get('operand_vus_checked')}/{r.get('operand_mismatched')} {r.get('problems') or r.get('why') or ''}",
              file=sys.stderr, flush=True)
        res.append(r)
    print(json.dumps(res, indent=1))
    return 0 if all(r["status"] == "BOUND" for r in res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
