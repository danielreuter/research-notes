"""red-team-standard-hash R1: the (vu, x, W) leaf triple of a hashed statement is chosen by the prover.

A v5 statement (`authentication = included-hash`, any leaf scheme: `+blake3`, `+poseidon2`, `+ajtai-*`) names per VU its
y leaf (`vu_index`), the x row it used (`x_index`) and the W column (`w_index`).  Both verifiers (Rust `auth::check_hashed`,
Python `hashauth.verify_hash_auth`) only check that those leaves open under the roots; neither derives `x_index` /
`w_index` from `vu_index` and the committed set's layout (unshared: x = W = vu; a tile: v // nw, v % nw).  So a committer
that serves a WRONG output y_v gets it accepted: prove VU v on any committed (row a, column b) whose product is y_v.

Here (2 VUs, l = 256): honest x rows and W columns (tree a and b roots equal the honest instance set's), VU 0's committed
output is VU 1's true output, the statement claims VU 0 on (x row 1, W column 1).  Checks, exit 0 iff all hold:
  * a / b roots equal the honest commitment's, y root differs (only the served output is wrong);
  * Python verify_vus ACCEPTS; Rust `verify` PINNED ACCEPTS; Rust `batch --target-bits 128` PINNED ACCEPTS;
  * reverify.verify_tree (the independent re-verification that writes verified=accepted) PASSES on the dump;
  * control: the same dishonest commitment with the honest mapping (x = W = vu) is REJECTED by Rust.

    python -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $LIGERO_VERIFY --out DIR [--relation fp8-ada --leaf blake3]
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    ap.add_argument("--target", type=float, default=-132.0, help="runner target log2 (l = 256 at -128 lands at 2^-127.88)")
    ap.add_argument("--mode", default="fiat-shamir")
    ap.add_argument("--zk", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--set-binding", action="store_true",
                    help="bind the trees to the relation's instance set (dataset, tier, instances_digest) as a producer does")
    args = ap.parse_args()

    from .. import protocol
    from ..hashauth import HashAuth
    from ..relations import relation
    from ..relchain import HashedRelationRunner, instances, instances_digest
    from ..serialize import _statement_of, proof_bytes, statement_bytes, system_bytes
    from .. import reverify as RV

    rel = relation(args.relation)
    n = args.vus
    base = instances(rel, n)
    y_true = [int(v[3]) for v in base]
    assert y_true[0] != y_true[1], "pick another seed: VU 0 and VU 1 share an output"

    def runner():
        return HashedRelationRunner(rel, args.device, args.target, zk=args.zk, mode=args.mode, leaf=args.leaf)

    bkw = ({"dataset": rel.instances_dataset, "tier": rel.instances_tier, "manifest_sha256": instances_digest(rel, n)}
           if args.set_binding else {})
    R = runner()
    R.commit_vus(base, **bkw)
    h_roots = {nm: R.trees[nm].ref.root.hex() for nm in "aby"}
    h_bind = {nm: R.trees[nm].ref.binding.hex() for nm in "aby"}

    served = list(base)
    served[0] = (base[0][0], base[0][1], base[0][2], base[1][3])      # VU 0's committed output: VU 1's true output
    R.commit_vus(served, **bkw)
    roots = {nm: R.trees[nm].ref.root.hex() for nm in "aby"}
    binds = {nm: R.trees[nm].ref.binding.hex() for nm in "aby"}

    out = Path(args.out)
    res = {"relation": R.relation, "sys_id": protocol.system_id(R.sys).hex(), "y_true": y_true,
           "y_committed": [int(v[3]) for v in served], "honest_roots": h_roots, "committed_roots": roots,
           "bindings_equal_honest": binds == h_bind}

    def emit(tag, vus, xi, wi):
        auth = HashAuth.for_vus(R.trees, list(range(n)), xi, wi)
        proof, pubs, lay = R.prove_vus(vus, check=False, vu_ids=list(range(n)), auth=auth, coins=None, min_l=args.min_l)
        ok, why = R.verify_vus(proof, pubs, lay, coins=None)
        d = out / tag
        (d / "rep0").mkdir(parents=True, exist_ok=True)
        st = _statement_of(R, pubs, lay, R.cfg(lay.l), 1)
        (d / "system.bin").write_bytes(system_bytes(R.sys))
        (d / "rep0" / "sub_00.stmt").write_bytes(statement_bytes(st))
        (d / "rep0" / "sub_00.proof").write_bytes(proof_bytes(proof))
        r = subprocess.run([args.bin, "verify", "--system", str(d / "system.bin"), "--statement", str(d / "rep0" / "sub_00.stmt"),
                            "--proof", str(d / "rep0" / "sub_00.proof")], capture_output=True, text=True)
        js = json.loads(r.stdout.strip().splitlines()[-1])
        (d / "verdict.json").write_text(json.dumps(js, indent=1))
        man = {"relation": rel.name, "mode": args.mode,
               "files": [{"proof": "rep0/sub_00.proof", "proof_sha256": _sha(d / "rep0" / "sub_00.proof"),
                          "stmt": "rep0/sub_00.stmt", "stmt_bytes": (d / "rep0" / "sub_00.stmt").stat().st_size}],
               "system_file": {"path": "system.bin", "sha256": _sha(d / "system.bin"), "bytes": (d / "system.bin").stat().st_size}}
        (d / "manifest.json").write_text(json.dumps(man, indent=1))
        v = RV.Verifier(Path(args.bin).resolve(), _sha(Path(args.bin)), None)
        rep = RV.Report(f"art:rtsh-{tag}")
        RV.verify_tree(d, man, v, rep, jobs=1, params={}, asserted=None, out_dir=d / "reverify")
        row = {"x_index": xi, "w_index": wi, "python": [bool(ok), why], "rust_accepted": js["accepted"],
               "rust_pinned": js.get("system_pinned"), "rust_reason": js["reason"][:160],
               "reverify": [rep.status, rep.why, rep.relation]}
        print(f"{tag}: x_index {xi} w_index {wi}: python {ok} {why!r}; rust accepted {js['accepted']} pinned "
              f"{js.get('system_pinned')} ({js['reason'][:100]}); reverify.verify_tree {rep.status} {rep.why} pinned={rep.relation}")
        return row

    remap = list(range(n))
    remap[0] = 1
    res["forgery"] = emit("forgery", [base[i] for i in remap], remap, remap)
    res["control"] = emit("control", base, list(range(n)), list(range(n)))

    ab_honest = all(roots[nm] == h_roots[nm] for nm in "ab")
    f, c = res["forgery"], res["control"]
    broke = (ab_honest and roots["y"] != h_roots["y"] and f["python"][0] and f["rust_accepted"] and f["rust_pinned"]
             and f["reverify"][0] == "PASS" and not c["rust_accepted"])
    res["verdict"] = "FORGERY ACCEPTED" if broke else "not reproduced"
    (out / "remap.json").write_text(json.dumps(res, indent=1, default=str))
    print(f"\na/b roots == honest: {ab_honest}; y root differs: {roots['y'] != h_roots['y']}; bindings == honest: {binds == h_bind}")
    print(f"VU 0: true y {y_true[0]}, committed y {served[0][3]} (VU 1's)")
    print("\n*** R1: wrong output under honest x/W roots ACCEPTED (python, rust pinned, reverify PASS); honest-mapping control "
          "rejected ***" if broke else "\n(not reproduced)")
    return 0 if broke else 1


if __name__ == "__main__":
    raise SystemExit(main())
