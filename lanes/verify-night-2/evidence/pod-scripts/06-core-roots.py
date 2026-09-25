"""verify-night-2: recompute the commitment roots a result's statements bind, from MY tree's instance set, with the core
reference only (verity.commitments), and compare them with the dumped statements' auth block and the run's commit-evidence.

For an `authentication = included-hash` result (Poseidon2 row leaves, leaf/v2h):
  x rows / W columns / y words: relchain.instances(rel, N) of my tree (what bench_vu_rel commits, untiled: VU i's own x row
  and W column); y word = rel.y_public(final accumulator).
  bindings: verity.commitments.identity_digest(hashauth.BINDING_TAG, {dataset, tier, manifest_sha256 = my tree's
  relchain.instances_digest, lo, hi, K, tree, schema}).
  leaves: verity.commitments.rowleaf.row_leaf_value(poseidon2_babybear.hash_row(row, word_bits, role)) for a / b; the
  word's big-endian bytes (schema u16 / u32) for y.  Trees: verity.commitments.merkle.MerkleTree over
  CommitmentDomain(binding, owner, RangeIndexedDomain(0, count)).

    python 06-core-roots.py ART...   (AWS_* read credential in the environment) -> JSON on stdout, one line per result on stderr
"""
import json
import os
import sys
import tempfile
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from verity.commitments import CommitmentDomain, MerkleTree, RangeIndexedDomain, identity_digest
from verity.commitments import poseidon2_babybear as p2
from verity.commitments.rowleaf import SCHEMA_ROW, row_leaf_value

from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.serialize import read_statement
from research.store.local import LocalStore

N = int(os.environ.get("VN2_N", 4096))
PROCS = int(os.environ.get("VY_CPU_THREADS", os.cpu_count() or 1))
OWNER = {"a": -1, "b": -2, "y": -1}
BINDING_TAG = "verity/ligero-b/auth-binding/v2h"  # hashauth.BINDING_TAG (checked below against the backend's constant)
_cache = {}


def _row_leaf(args):
    words, word_bits, role = args
    return row_leaf_value(p2.hash_row([int(w) for w in words], word_bits, role))


def core_trees(rel_name: str):
    if rel_name in _cache:
        return _cache[rel_name]
    from backends.direct.ligero import hashauth, hashchain
    assert hashauth.BINDING_TAG == BINDING_TAG, hashauth.BINDING_TAG
    base = rel_name.split("+")[0]
    rel = RELATIONS[base]
    data = relchain.instances(rel, N, procs=PROCS)
    msha = relchain.instances_digest(rel, N)
    K = getattr(rel, "vu_words", relchain.K_VU)
    word_bits = hashchain.compose(rel, None).word_bits
    ysch, ynb = hashauth.word_schema(rel.y_bits)
    x_rows = [np.asarray(v[0]).reshape(-1) for v in data]
    w_cols = [np.asarray(v[1]).reshape(-1) for v in data]
    y = [int(rel.y_public(int(v[3]))) for v in data]
    info = {"relation": base, "dataset": rel.instances_dataset, "tier": rel.instances_tier, "manifest_sha256": msha, "K": K,
            "word_bits": word_bits, "y_schema": ysch}
    out = {}
    with Pool(PROCS) as pool:
        for n, rows, role in (("a", x_rows, p2.ROLE_X), ("b", w_cols, p2.ROLE_W), ("y", None, None)):
            schema = SCHEMA_ROW if n != "y" else ysch
            binding = bytes.fromhex(identity_digest(BINDING_TAG, {"dataset": rel.instances_dataset, "tier": rel.instances_tier,
                                                                  "manifest_sha256": msha, "lo": 0, "hi": N, "K": int(K),
                                                                  "tree": n, "schema": schema}))
            if n == "y":
                values = [w.to_bytes(ynb, "big") for w in y]
            else:
                values = pool.map(_row_leaf, [(r, word_bits, role) for r in rows], chunksize=16)
            dom = CommitmentDomain(binding, OWNER[n], RangeIndexedDomain(0, len(values)))
            t = MerkleTree(dom, dict(enumerate(values)), lambda _p, s=schema: s)
            out[n] = {"binding": binding.hex(), "owner": OWNER[n], "count": len(values), "root": t.commitment.root.hex()}
    _cache[rel_name] = (info, out)
    return info, out


def check(st, art):
    m = st.get_manifest(art)
    tree = (m.refs or {}).get("run_files")
    res = {"result": art, "run_files": tree}
    ev = (((m.meta or {}).get("validation") or {}).get("evidence") or {}).get("commit", {}).get("evidence", {})
    with tempfile.TemporaryDirectory(dir="/workspace/verify-night-2") as td:
        d = Path(st.fetch(tree, Path(td) / "t", paths=["*manifest.json", "*.stmt", "*commit-evidence.json"]))
        mans = sorted(d.rglob("manifest.json"))
        pman = [p for p in mans if "proofs" in p.parts] or mans
        man = json.loads(pman[0].read_text())
        rel_name = man["relation"]["name"] if isinstance(man.get("relation"), dict) else man.get("relation")
        ce = sorted(d.rglob("commit-evidence.json"))
        ce_trees = json.loads(ce[0].read_text()).get("trees") if ce else None
        info, core = core_trees(str(rel_name))
        res.update({"relation": rel_name, "core": core, "info": info})
        problems = []
        for src, trees in (("result-meta commit evidence", ev.get("trees")), ("commit-evidence.json", ce_trees)):
            if not trees:
                problems.append(f"{src}: absent")
                continue
            for n in ("a", "b", "y"):
                for k in ("binding", "owner", "count", "root"):
                    if str(trees[n][k]) != str(core[n][k]):
                        problems.append(f"{src} {n}.{k}: {trees[n][k]} != core {core[n][k]}")
        n_stmt = 0
        covered = set()
        for f in man.get("files", []):
            if not f.get("stmt"):
                continue
            lo, hi = f["vus"]
            s = read_statement((pman[0].parent / f["stmt"]).read_bytes())
            n_stmt += 1
            ha = s.hash_auth
            if ha is None:
                problems.append(f"{f['stmt']}: no hash_auth block")
                continue
            for t in ha.trees:
                c = core[t.name]
                if (t.binding.hex(), t.owner, t.count, t.root.hex()) != (c["binding"], c["owner"], c["count"], c["root"]):
                    problems.append(f"{f['stmt']} tree {t.name}: {t.to_json()} != core")
            vi, xi, wi = list(ha.vu_index), list(ha.x_index), list(ha.w_index)
            if vi != list(range(lo, hi)) or xi != vi or wi != vi:
                problems.append(f"{f['stmt']}: leaf indices not the untiled VU range [{lo},{hi})")
            covered.update(vi)
            if len(problems) > 8:
                break
        res.update({"statements": n_stmt, "vus_covered": len(covered), "problems": problems[:12]})
        res["status"] = "ROOTS-MATCH" if not problems and len(covered) == N else "MISMATCH"
    return res


def main(arts):
    st = LocalStore()
    out = []
    for a in arts:
        try:
            r = check(st, a)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            r = {"result": a, "status": "ERROR", "why": f"{type(e).__name__}: {e}"}
        print(f"# {a[:16]} {r['status']} {r.get('relation')} stmts={r.get('statements')} vus={r.get('vus_covered')} "
              f"roots a={r.get('core', {}).get('a', {}).get('root', '')[:8]} b={r.get('core', {}).get('b', {}).get('root', '')[:8]} "
              f"y={r.get('core', {}).get('y', {}).get('root', '')[:8]} {r.get('problems') or r.get('why') or ''}", file=sys.stderr, flush=True)
        out.append(r)
    print(json.dumps(out, indent=1))
    return 0 if all(r["status"] == "ROOTS-MATCH" for r in out) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
