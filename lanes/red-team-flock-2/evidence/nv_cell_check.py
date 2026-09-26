#!/usr/bin/env python3
"""red-team-flock-2: a verity/flock-pure-block/v2 fp4-nvf4 cell's verifier-written instance files (flock-pure-instances/v1)
checked against its NVFP4 input set, with verity core only (rowleaf NVFP4 rows and digests, merkle trees, the
BLACKWELL_SM120_NVF4 model), never flock-backend's writer:

- the header: relation fp4-nvf4, k 1536, 24 units, 4-bit words, 864-byte rows, the NVFP4 row schema, the set and range;
- the rows are nvfp4_row_bytes of the set's codes and scales for the range;
- the 24 accumulators per VU are my own step_scaled chain, and out = y = the set's recorded y = the last accumulator;
- the row digests (blake3 or sha256 row-nvfp4), the y word leaves and the three roots recompute; the domain ids are
  CommitmentDomain(binding, owner, [0, n)), and the bindings are hashauth.binding_digest(set, tier, content digest, range,
  K, tree, schema).

  nv_cell_check.py SET_DIR FILE... [--procs N]
"""
import json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

K, U = 1536, 24


def chain(args):
    from verity.ml.tc.models import BLACKWELL_SM120_NVF4 as M
    x, w, sx, sw = args
    out = []
    for a, b, sa, sb in zip(x.tolist(), w.tolist(), sx.tolist(), sw.tolist()):
        c, row = 0, []
        for s in range(U):
            c = M.step_scaled(c, a[64 * s:64 * s + 64], b[64 * s:64 * s + 64], sa[4 * s:4 * s + 4], sb[4 * s:4 * s + 4])
            row.append(c)
        out.append(row)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    if "--procs" in sys.argv:
        args.remove(sys.argv[sys.argv.index("--procs") + 1])
    set_dir, files = Path(args[0]), args[1:]
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from verity.commitments.indexed import RangeIndexedDomain
    from verity.commitments.merkle import CommitmentDomain, tree_levels
    from verity.commitments.rowleaf import (ROLE_W, ROLE_X, SCHEMA_BLAKE3_ROW_NVFP4, SCHEMA_SHA256_ROW_NVFP4, blake3_row_nvfp4_digest,
                                            nvfp4_row_bytes, sha256_row_nvfp4_digest)
    from ligero import auth, hashauth
    man = json.loads((set_dir / "manifest.json").read_text())
    P = man["ports"]
    arr = {r: np.fromfile(set_dir / P[r]["file"], dtype={"u8": "u1", "u32": "<u4"}[P[r]["dtype"]]).reshape(-1, int(P[r]["words"]))
           for r in ("x", "w", "sx", "sw", "y")}
    heads = []
    for f in files:
        b = open(f, "rb").read()
        nl = b.index(b"\n")
        heads.append((f, json.loads(b[:nl]), b[nl + 1:]))
    hi_all = max(h["instances"]["range"][1] for _, h, _ in heads)
    step = max(1, hi_all // (8 * procs))
    jobs = [(arr["x"][i:i + step], arr["w"][i:i + step], arr["sx"][i:i + step], arr["sw"][i:i + step]) for i in range(0, hi_all, step)]
    with ProcessPoolExecutor(procs) as ex:
        accs_all = np.asarray([r for part in ex.map(chain, jobs) for r in part], dtype=np.uint32)
    y_set = arr["y"][:hi_all, 0]
    print(f"SET {set_dir}: {man['set']} content {man['content_digest'][:16]}; my BLACKWELL_SM120_NVF4 chain over VUs [0, {hi_all}): "
          f"last accumulator == the set's y on {int((accs_all[:, -1] == y_set).sum())} of {hi_all}", flush=True)
    for f, h, body in heads:
        lo, hi = h["instances"]["range"]
        n = hi - lo
        rb = K // 2 + K // 16
        hdr = (h["relation"], h["k"], h["units"], h["word_bits"], h["row_bytes"], h["epilogue"], h["vus"]) == ("fp4-nvf4", K, U, 4, rb, False, n)
        sch = h["schemas"]["a"]
        dig = {SCHEMA_BLAKE3_ROW_NVFP4: blake3_row_nvfp4_digest, SCHEMA_SHA256_ROW_NVFP4: sha256_row_nvfp4_digest}[sch]
        x, w, sx, sw = (arr[r][lo:hi] for r in ("x", "w", "sx", "sw"))
        rx = b"".join(nvfp4_row_bytes(c.tolist(), s.tolist()) for c, s in zip(x, sx))
        rw = b"".join(nvfp4_row_bytes(c.tolist(), s.tolist()) for c, s in zip(w, sw))
        at = 0
        f_rx, at = body[at:at + n * rb], at + n * rb
        f_rw, at = body[at:at + n * rb], at + n * rb
        f_acc = np.frombuffer(body[at:at + 4 * n * U], "<u4").reshape(n, U); at += 4 * n * U
        f_out = np.frombuffer(body[at:at + 4 * n], "<u4"); at += 4 * n
        f_y = np.frombuffer(body[at:at + 4 * n], "<u4"); at += 4 * n
        acc = accs_all[lo:hi]
        body_ok = at == len(body)
        ref = h["instances"]
        set_ok = ref["dataset"] == man["set"] and ref["manifest_sha256"] == man["content_digest"]
        da = [dig(c.tolist(), s.tolist(), ROLE_X) for c, s in zip(x, sx)]
        db = [dig(c.tolist(), s.tolist(), ROLE_W) for c, s in zip(w, sw)]
        ysch, ybytes = hashauth.word_schema(32)
        schemas = {"a": sch, "b": sch, "y": ysch}
        bind_ok, roots_ok, dom_ok = True, {}, True
        y = [int(v) for v in acc[:, -1]]
        for t, leaves_of in (("a", da), ("b", db), ("y", y)):
            bnd = hashauth.binding_digest(dataset=ref["dataset"], tier=ref["tier"], manifest_sha256=ref["manifest_sha256"], lo=lo, hi=hi,
                                          K=K, tree=t, schema=schemas[t])
            bind_ok &= bnd.hex() == h["bindings"][t]
            dom = CommitmentDomain(bnd, auth.OWNER[t], RangeIndexedDomain(0, n))
            dom_ok &= dom.domain_id.hex() == h["domain_ids"][t]
            if t == "y":
                leaves = [dom.leaf(r, r, ysch, v.to_bytes(ybytes, "big")) for r, v in enumerate(leaves_of)]
            else:
                leaves = [dom.leaf(r, r, sch, d) for r, d in enumerate(leaves_of)]
            roots_ok[t] = tree_levels(dom, leaves)[-1][0].hex() == h["roots"][t]
        print(f"FILE {f.split('/verifier/')[-1]}: [{lo}, {hi}) schema {sch}; header fields {hdr}; set {set_ok}; body length {body_ok}; "
              f"rows x/w == nvfp4_row_bytes of the set {f_rx == rx}/{f_rw == rw}; accumulators == my chain {bool((f_acc == acc).all())}; "
              f"out == y == set y == last accumulator {bool((f_out == f_y).all() and (f_y == y_set[lo:hi]).all() and (f_y == acc[:, -1]).all())}; "
              f"bindings {bind_ok}; domain ids {dom_ok}; roots {roots_ok}", flush=True)


if __name__ == "__main__":
    main()
