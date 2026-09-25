"""red-team-standard-hash R4: an R2 coverage check that counts statements the verifier never checks a proof for.

The R2 fixes require each rep's statements to cover [0, total) exactly once.  Rust `batch --dir` verifies every `*.proof`
with its `*.stmt`; a statement without a proof is never verified.  So coverage computed from statements alone can be
satisfied by a statement whose proof was never made (here: made, then deleted, so its bytes are an honest statement).

Honest set of N VUs (production instance-set bindings), one sub-batch per VU, rep0/sub_<v>.{stmt,proof}.  Variants:
  * control      -- every proof present, manifest lists all: must PASS;
  * orphan-stmt  -- only VU 0 proven (re-proved with n_proofs = 1, so the Rust batch's count agrees); the other VUs'
                    honest statements stay without their proofs; the manifest lists only sub_00
                    (reverify.commitment_problems globs rep*/*.stmt);
  * stmt-entry   -- the same files; the manifest also lists the unproven statements with no proof (a check that walks
                    the manifest's `stmt` entries, e.g. verify-night-2's 06-core-roots.py).
Each variant: reverify.verify_tree (whatever commitment check the tree carries); the dir is kept for other checkers.
Exit 0 iff the control passes and some variant passes reverify with fewer VUs proven than covered.

    python -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $LIGERO_VERIFY --out DIR [--vus 2]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--relation", default="fp8-ada")
    ap.add_argument("--leaf", default="blake3")
    ap.add_argument("--vus", type=int, default=2)
    ap.add_argument("--min-l", type=int, default=256)
    ap.add_argument("--target", type=float, default=-132.0)
    ap.add_argument("--mode", default="fiat-shamir")
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    from .. import reverify as RV
    from ..hashauth import HashAuth
    from ..relations import relation
    from ..relchain import HashedRelationRunner, instances, instances_digest
    from ..serialize import _statement_of, proof_bytes, statement_bytes, system_bytes

    rel = relation(args.relation)
    n = args.vus
    base = instances(rel, n)
    msha = instances_digest(rel, n)
    R = HashedRelationRunner(rel, args.device, args.target, zk=False, mode=args.mode, leaf=args.leaf)
    R.commit_vus(base, dataset=rel.instances_dataset, tier=rel.instances_tier, manifest_sha256=msha)
    out = Path(args.out)
    full = out / "full"
    (full / "rep0").mkdir(parents=True, exist_ok=True)
    (full / "system.bin").write_bytes(system_bytes(R.sys))
    def prove(v: int, n_proofs: int, d: Path) -> str:
        auth = HashAuth.for_vus(R.trees, [v], [v], [v])
        proof, pubs, lay = R.prove_vus([base[v]], check=False, vu_ids=[v], auth=auth, coins=None, min_l=args.min_l)
        ok, why = R.verify_vus(proof, pubs, lay, coins=None)
        assert ok, why
        st = _statement_of(R, pubs, lay, R.cfg(lay.l), n_proofs)
        name = f"sub_{v:02d}"
        (d / "rep0" / f"{name}.stmt").write_bytes(statement_bytes(st))
        (d / "rep0" / f"{name}.proof").write_bytes(proof_bytes(proof))
        return name

    # the honest dump: every statement names n_proofs = n (the rep's batch size); the forger's re-proves the VUs it keeps
    # with n_proofs = how many it keeps, so the Rust batch's proof count agrees with them
    subs = [prove(v, n, full) for v in range(n)]
    kept = out / "kept"
    (kept / "rep0").mkdir(parents=True, exist_ok=True)
    prove(0, 1, kept)

    def entry(d: Path, name: str, v: int, with_proof: bool) -> dict:
        e = {"rep": 0, "vus": [v, v + 1], "stmt": f"rep0/{name}.stmt", "stmt_bytes": (d / "rep0" / f"{name}.stmt").stat().st_size}
        if with_proof:
            e |= {"proof": f"rep0/{name}.proof", "proof_sha256": _sha(d / "rep0" / f"{name}.proof")}
        return e

    def variant(tag: str, drop: set[int], list_dropped_stmt: bool) -> dict:
        d = out / tag
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(full, d)
        for v in drop:
            (d / "rep0" / f"{subs[v]}.proof").unlink()
        if drop:
            for v in set(range(n)) - drop:
                for ext in ("stmt", "proof"):
                    shutil.copy(kept / "rep0" / f"{subs[v]}.{ext}", d / "rep0" / f"{subs[v]}.{ext}")
        files = [entry(d, subs[v], v, True) for v in range(n) if v not in drop]
        if list_dropped_stmt:
            files += [entry(d, subs[v], v, False) for v in sorted(drop)]
        man = {"relation": {"name": R.relation}, "mode": args.mode, "files": files,
               "set": {"total_vus": n, "instances": msha},
               "system_file": {"path": "system.bin", "sha256": _sha(d / "system.bin"), "bytes": (d / "system.bin").stat().st_size}}
        (d / "manifest.json").write_text(json.dumps(man, indent=1))
        v = RV.Verifier(Path(args.bin).resolve(), _sha(Path(args.bin)), None)
        rep = RV.Report(f"art:rtsh-{tag}")
        RV.verify_tree(d, man, v, rep, jobs=1, params={}, asserted=None, out_dir=d / "reverify")
        proven = n - len(drop)
        row = {"proofs": proven, "statements": n, "reverify": [rep.status, rep.why, rep.relation],
               "hashed_checked": getattr(rep, "hashed", None), "reps": {k: {kk: x.get(kk) for kk in ("n", "batch_accepted", "system_pinned")}
                                                                      for k, x in rep.reps.items()}}
        print(f"{tag}: {proven}/{n} VUs proven, {n} statements; reverify {rep.status} {rep.why} "
              f"(commitment check ran: {row['hashed_checked']}) reps {row['reps']}", flush=True)
        return row

    has_r2 = hasattr(RV, "commitment_problems")
    res = {"relation": R.relation, "n": n, "instances_digest": msha, "reverify_has_commitment_check": has_r2,
           "roots": {nm: R.trees[nm].ref.root.hex() for nm in "aby"},
           "control": variant("control", set(), False),
           "orphan-stmt": variant("orphan-stmt", set(range(1, n)), False),
           "stmt-entry": variant("stmt-entry", set(range(1, n)), True)}
    broke = [t for t in ("orphan-stmt", "stmt-entry") if res[t]["reverify"][0] == "PASS"]
    ok = res["control"]["reverify"][0] == "PASS" and bool(broke)
    res["verdict"] = f"PASS with {n - 1} of {n} VUs unproven: {broke}" if ok else "not reproduced"
    (out / "orphan.json").write_text(json.dumps(res, indent=1, default=str))
    print(res["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
