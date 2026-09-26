#!/usr/bin/env python3
"""red-team-flock-2: an independent `flock-pure-instances/v1` writer for fp4-nvf4 (NVFP4, k = 1536, 864-byte rows).

Rows, digests and trees come from `verity.commitments` (rowleaf NVFP4, merkle), accumulators from
`verity.ml.tc.models.BLACKWELL_SM120_NVF4.step_scaled`; nothing is shared with flock-backend's or flock-gpu-link's writers.
Scales vary per 16-code group (so a permuted scale wiring changes the output). VU 0 plants zero-code groups (x group 0
of units 5 and 20, W group 1 of unit 7, scale 0x38) so a scale-operand flip there leaves the unit's output unchanged.

  gen_fp4.py OUT --vus N --scheme blake3|sha256 [--seed S] [--tamper none|y|relabel]
  gen_fp4.py OUT --vus N --shape fp8 --free-scale 38383838      (1536-byte code-only rows, 48 units: the G2 misconfiguration)
"""
import argparse, hashlib, json, random, sys

from verity.commitments.indexed import RangeIndexedDomain
from verity.commitments.merkle import CommitmentDomain, tree_levels
from verity.commitments.rowleaf import (SCHEMA_BLAKE3_ROW, SCHEMA_BLAKE3_ROW_NVFP4, SCHEMA_SHA256_ROW_NVFP4,
                                        blake3_row_key, blake3_row_nvfp4_digest, nvfp4_row_bytes, sha256_row_nvfp4_digest)
from verity.commitments import blake3 as b3ref
from verity.ml.tc.models import BLACKWELL_SM120_NVF4 as M

K, G = 1536, 16
PLANT = {(5, "x", 0), (20, "x", 0), (7, "w", 1)}


def scale(rng):
    r = rng.random()
    if r < 0.03:
        return 0x00
    return rng.randrange(0x01, 0x7F)          # UE4M3, padding bit 0, never 0x7F


def row(rng, v, role, units):
    codes = [rng.randrange(16) for _ in range(64 * units)]
    scales = [scale(rng) for _ in range(4 * units)]
    if v == 0 and units == 24:
        for u, r, g in PLANT:
            if r == role:
                for i in range(64 * u + 16 * g, 64 * u + 16 * g + 16):
                    codes[i] = 0
                scales[4 * u + g] = 0x38
    return codes, scales


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--vus", type=int, required=True)
    ap.add_argument("--scheme", choices=["blake3", "sha256"], default="blake3")
    ap.add_argument("--seed", type=int, default=20260926)
    ap.add_argument("--tamper", choices=["none", "y", "relabel"], default="none")
    ap.add_argument("--shape", choices=["fp4", "fp8"], default="fp4")
    ap.add_argument("--free-scale", default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    fp8 = a.shape == "fp8"
    units, row_bytes = (48, 1536) if fp8 else (24, 864)
    free = bytes.fromhex(a.free_scale) if fp8 else None     # the 4 scale bytes every unit uses (LE word order), both roles
    X, W, accs, out = [], [], [], []
    for v in range(a.vus):
        xc, xs = row(rng, v, "x", units)
        wc, ws = row(rng, v, "w", units)
        if fp8:
            xs, ws = list(free) * units, list(free) * units
        c, acc = 0, []
        for u in range(units):
            c = M.step_scaled(c, xc[64 * u:64 * u + 64], wc[64 * u:64 * u + 64], xs[4 * u:4 * u + 4], ws[4 * u:4 * u + 4])
            acc.append(c)
        if v == 0 and not fp8:
            for u, r, g in PLANT:          # the isolation premise: flipping the planted scale's bit 0 leaves the step's output
                args = [0 if u == 0 else acc[u - 1], xc[64 * u:64 * u + 64], wc[64 * u:64 * u + 64], list(xs[4 * u:4 * u + 4]), list(ws[4 * u:4 * u + 4])]
                args[3 if r == "x" else 4][g] ^= 1
                assert M.step_scaled(*args) == acc[u], (u, r, g)
        if fp8:
            xr = bytes(xc[2 * i] | (xc[2 * i + 1] << 4) for i in range(len(xc) // 2))
            wr = bytes(wc[2 * i] | (wc[2 * i + 1] << 4) for i in range(len(wc) // 2))
        else:
            xr, wr = nvfp4_row_bytes(xc, xs), nvfp4_row_bytes(wc, ws)
        assert len(xr) == len(wr) == row_bytes
        X.append((xr, xc, xs)); W.append((wr, wc, ws)); accs.append(acc); out.append(acc[-1])
    y = list(out)
    if a.tamper == "y":
        y[0] ^= 1
    if fp8:
        sch = SCHEMA_BLAKE3_ROW
        dig = lambda r, role: b3ref.keyed(blake3_row_key(role), r[0])
    elif a.scheme == "sha256":
        sch = SCHEMA_SHA256_ROW_NVFP4
        dig = lambda r, role: sha256_row_nvfp4_digest(r[1], r[2], role)
    else:
        sch = SCHEMA_BLAKE3_ROW if a.tamper == "relabel" else SCHEMA_BLAKE3_ROW_NVFP4
        dig = lambda r, role: blake3_row_nvfp4_digest(r[1], r[2], role)
    schemas = {"a": sch, "b": sch, "y": "u32"}
    n = a.vus
    bind = {t: hashlib.sha256(f"red-team-flock-2/gen_fp4/{t}/{a.seed}/{a.shape}/{a.scheme}/{n}".encode()).digest() for t in "aby"}
    dom = {t: CommitmentDomain(bind[t], -1, RangeIndexedDomain(0, n)) for t in "aby"}
    leaves = {"a": [dom["a"].leaf(r, r, sch, dig(X[r], 1)) for r in range(n)],
              "b": [dom["b"].leaf(r, r, sch, dig(W[r], 2)) for r in range(n)],
              "y": [dom["y"].leaf(r, r, "u32", y[r].to_bytes(4, "big")) for r in range(n)]}
    roots = {t: tree_levels(dom[t], leaves[t])[-1][0].hex() for t in "aby"}
    header = {"format": "flock-pure-instances/v1", "relation": "fp4-nvf4", "vus": n, "k": K, "word_bits": 4, "units": units,
              "row_bytes": row_bytes, "epilogue": False,
              "instances": {"generator": "red-team-flock-2/gen_fp4.py", "seed": a.seed, "shape": a.shape, "tamper": a.tamper,
                            "free_scale": a.free_scale},
              "roots": roots, "domain_ids": {t: dom[t].domain_id.hex() for t in "aby"}, "bindings": {t: bind[t].hex() for t in "aby"},
              "owners": {t: -1 for t in "aby"}, "schemas": schemas, "y_bytes": 4}
    le = lambda ws: b"".join(int(w).to_bytes(4, "little") for w in ws)
    with open(a.out, "wb") as f:
        f.write(json.dumps(header, sort_keys=True).encode() + b"\n")
        f.write(b"".join(r[0] for r in X)); f.write(b"".join(r[0] for r in W))
        f.write(b"".join(le(acc) for acc in accs)); f.write(le(out)); f.write(le(y))
    zero = sum(1 for acc in accs if acc[-1] in (0, 0x80000000))
    print(json.dumps({"out": a.out, "vus": n, "shape": a.shape, "schemas": schemas, "tamper": a.tamper, "roots": roots,
                      "out0": f"{out[0]:08x}", "y0": f"{y[0]:08x}", "zero_outputs": zero}))


if __name__ == "__main__":
    sys.exit(main())
