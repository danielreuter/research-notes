"""agkr-bound: the map from the unit operand bits (the link's prime side) to the row-leaf message bits (its binary
side), for the frozen honest witness.  Tests which unit order the generator uses (VU-major u = v * U + s or
slice-major u = s * N + v, U = K / k units per VU, unit s consuming words k*s .. k*s + k - 1 of x row v and W column v)
and whether every operand word appears in exactly one unit, i.e. whether the link map is a bijection.  Then states
the message-side offsets of the leaf layouts (prefix block, padding, word byte order).

    [REL=bf16-ampere LEAF=sha256] python 27_layout.py STMT OUT [N] [THREADS]      (cwd backends/gkr)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import bench_result as br                              # noqa: E402
from gpu import commit as CM                           # noqa: E402
from gpu.circuit import parse_circuit                  # noqa: E402

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
NT = int(sys.argv[4]) if len(sys.argv) > 4 else 13
REL, LEAF = os.environ.get("REL", "bf16-ampere"), os.environ.get("LEAF", "sha256")
FP8 = REL.startswith("fp8")
BITS = 8 if FP8 else 16
OUT.mkdir(parents=True, exist_ok=True)
names = parse_circuit((S / "circuit.txt").read_text()).col_names
k = (names.index("y.s") - 5) // 2
src = Path(br.__file__).resolve().parents[2]
frozen = src / "fixtures" / "bench-instances" / "v1" / "manifest.json"

from gpu.v2.fp8 import relation_params                 # noqa: E402
from gpu.v2.witness import Generator, Ops              # noqa: E402
from verity.commitments.frame_v3 import RowLeaf        # noqa: E402
from verity.commitments.rowleaf import ROLE_W, ROLE_X  # noqa: E402

if REL == "bf16-ampere":
    from verity_numerical.checker import REAL          # noqa: E402

    x, W, y0, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), frozen, br.TIER, 0, N)
    params = REAL
else:
    x, W, y0, rel = br.load_relation(REL, src, 0, N, NT)
    params = relation_params(rel)[0]
X = np.asarray(x).astype(np.int64).reshape(N, -1)
Wm = np.asarray(W).astype(np.int64).reshape(N, -1)
K = X.shape[1]
ops = Ops("cuda")
rows = Generator(ops, params).run(ops.asarray(np.array(x, dtype=np.uint16)), ops.asarray(W), ops.asarray(y0))
assert int(rows.bad.sum()) == 0
units = rows.units
nu = units.shape[0]
U = K // k
ux = units[:, 5:5 + k].long().cpu().numpy()
uw = units[:, 5 + k:5 + 2 * k].long().cpu().numpy()
res = {"relation": REL, "leaf": LEAF, "vus": N, "K": K, "k": k, "units": int(nu), "units_per_vu": U, "bits_per_word": BITS,
       "link_bits": int(nu * 2 * k * BITS), "message_bits": int(2 * N * K * BITS)}
orders = {}
if nu == N * U:
    for name in ("vu_major", "slice_major"):
        v, s = np.divmod(np.arange(nu), U) if name == "vu_major" else np.divmod(np.arange(nu), N)[::-1]
        cols = s[:, None] * k + np.arange(k)[None, :]
        orders[name] = {"x": bool((ux == X[v[:, None], cols]).all()), "w": bool((uw == Wm[v[:, None], cols]).all())}
res["orders"] = orders
match = [n for n, o in orders.items() if o["x"] and o["w"]]
res["order"] = match[0] if match else None
if not match:
    # fall back: where do the first units' operand words sit (first occurrence in x / W)
    res["sample"] = [{"unit": u, "x_positions": [[int(a) for a in np.argwhere(X == int(val))[:1].reshape(-1)] for val in ux[u, :4]]}
                     for u in range(3)]
res["bijection"] = bool(match) and res["link_bits"] == res["message_bits"]
lay = {}
for role, rn in ((ROLE_X, "x"), (ROLE_W, "w")):
    rl = RowLeaf(LEAF, role, BITS, K)
    L = rl.layout()
    lay[rn] = {"schema": rl.schema, "hash": L.hash, "prefix_bytes": len(L.prefix), "prefix_hex": L.prefix.hex(),
               "value_bytes": K * BITS // 8, "layout": repr(L)[:400]}
res["leaf_layout"] = lay
if LEAF == "sha256":
    rb, pb = K * BITS // 8, lay["x"]["prefix_bytes"]
    tail = (pb + rb) % 64
    res["sha256_message"] = {"prefix_bytes": pb, "value_offset_bits": 8 * pb, "value_block_aligned": pb % 64 == 0,
                             "compressions": (pb + rb + 9 + 63) // 64, "tail_bytes_in_last_value_block": tail,
                             "word_byte_order": "row words little-endian; SHA-256 schedule words big-endian 32-bit"}
print(json.dumps(res, indent=1, default=str), flush=True)
(OUT / "layout.json").write_text(json.dumps(res, indent=1, default=str))
