"""flock-bench-80gb: export the census unit circuit (internal/binary-census/unit.py) as a Flock canonical R1CS netlist.

Row i of the netlist is committed bit z_i with (A_i . z) * (B_i . z) = z_i (C = I). Layout:
  [0, n_in)                 inputs x | w | c, in the census's allocation order; A = [i] (xor an attached assertion), B = [const]
  [n_in, n_in + n_and)      the live ANDs in allocation order (topological)
  [.., + n_copy)            c_out bits that are not a single committed bit: A = form, B = [const]
  const = useful - 1        A = B = [const]  (pinned to 1 by Flock's const-wire pin)
Assertion j (a form L that must be 0) is folded into input row j: A_j = {j} xor L, so the row reads z_j + L = z_j,
i.e. L = 0, at no extra committed bit.

Also writes bit-exact test vectors against verity.ml.tc: valid cases (expected c_out from pipeline.step) and
non-finite negatives (some row must fail).

usage: python3.12 export_unit.py OUTDIR [ampere_bf16 hopper_bf16 hopper_e4m3 ...]
"""
from __future__ import annotations

import os
import random
import sys

CENSUS = os.environ.get(
    "CENSUS_DIR",
    "/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/"
    "bc-36415049-30db-4fff-a34b-81f0afc0124d/files/internal/binary-census",
)
sys.path.insert(0, os.environ.get("VERITY_SRC", "/Users/danielreuter/projects/verity-main-wt/main/packages/verity/src"))
sys.path.insert(0, CENSUS)

from verity.ml.tc.models import ADA_E4M3_M16N8K32, AMPERE_BF16_M16N8K16, HOPPER_BF16_M16N8K16, HOPPER_E4M3_K32  # noqa: E402

import test_unit as TU  # noqa: E402
import unit as U  # noqa: E402

TABLE = {
    "ampere_bf16": (AMPERE_BF16_M16N8K16, U.BF16),
    "hopper_bf16": (HOPPER_BF16_M16N8K16, U.BF16),
    "ada_e4m3": (ADA_E4M3_M16N8K32, U.E4M3),
    "hopper_e4m3": (HOPPER_E4M3_K32, U.E4M3),
}
K_LOG = 13


def export(name, outdir, n_valid=512, seed=11):
    pipeline, fmt = TABLE[name]
    C = U.unit(fmt, pipeline.groups, pipeline.width, pipeline.zero_exponent)
    cnt = C.counts()
    live = C.live()
    ins = [v for bits in C.inputs.values() for w in bits for v in w.s]
    assert ins == list(range(len(ins))), "inputs must be allocated first"
    n_in = len(ins)
    ands = sorted(v for v in live if C.kind[v] == "and")
    new = {v: i for i, v in enumerate(ins)}
    for v in ands:
        new[v] = len(new)
    outs = C.outputs["c_out"]
    copies = [w for w in outs if not (len(w.s) == 1 and w.c == 0)]
    useful = n_in + len(ands) + len(copies) + 1
    assert useful <= 1 << K_LOG, useful
    cpos = useful - 1

    def form(w):
        s = sorted(new[v] for v in w.s)
        return s + [cpos] if w.c else s

    rows = [None] * useful
    for i in range(n_in):
        rows[i] = ("i", [i], [cpos])
    assert len(C.asserts) <= n_in
    for j, (_, L) in enumerate(C.asserts):
        a = set(rows[j][1]) ^ set(form(L))
        rows[j] = ("i", sorted(a), [cpos])
    for v in ands:
        a, b = C.data[v]
        rows[new[v]] = ("a", form(a), form(b))
    out_pos = []
    ci = n_in + len(ands)
    for w in outs:
        if len(w.s) == 1 and w.c == 0:
            out_pos.append(new[next(iter(w.s))])
        else:
            rows[ci] = ("c", form(w), [cpos])
            out_pos.append(ci)
            ci += 1
    rows[cpos] = ("k", [cpos], [cpos])
    nnz = sum(len(r[1]) + len(r[2]) for r in rows)

    # test vectors
    rng = random.Random(seed)
    k = pipeline.k
    rand_op = TU.rand_bf16 if fmt is U.BF16 else TU.rand_e4m3
    nb = fmt.bits
    cases = []
    while len(cases) < n_valid:
        if rng.random() < 0.15:
            xs, ws = TU.cancel_case(rng, k, rand_op, nb)
        else:
            xs = [rand_op(rng) for _ in range(k)]
            ws = [rand_op(rng) for _ in range(k)]
        c = TU.rand_acc(rng)
        try:
            ref = pipeline.step(c, xs, ws)
        except Exception:
            continue
        cases.append(("v", xs, ws, c, ref))
    rng = random.Random(seed + 1)
    for t in range(64):
        xs = [rand_op(rng) for _ in range(k)]
        ws = [rand_op(rng) for _ in range(k)]
        c = TU.rand_acc(rng)
        kind = t % 3
        if kind == 0:
            i = rng.randrange(k)
            xs[i] = ((rng.getrandbits(1) << 15) | (0xFF << 7) | rng.getrandbits(7)) if fmt is U.BF16 else (0x7F | (rng.getrandbits(1) << 7))
        elif kind == 1:
            c = (rng.getrandbits(1) << 31) | (0xFF << 23) | rng.getrandbits(23)
        else:
            if fmt is U.BF16:
                ws[rng.randrange(k)] = 0x7F80 | (rng.getrandbits(1) << 15)
            else:
                ws[rng.randrange(k)] = 0xFF
        cases.append(("n", xs, ws, c, 0))

    def inbits(xs, ws, c):
        v = 0
        pos = 0
        for arr in (xs, ws):
            for x in arr:
                v |= x << pos
                pos += nb
        v |= c << pos
        pos += 32
        assert pos == n_in
        return v.to_bytes((n_in + 7) // 8, "little").hex()

    path = os.path.join(outdir, f"unit-{name}.netlist")
    with open(path, "w") as f:
        f.write("FLOCKUNIT 1\n")
        f.write(f"pipeline {name}\nk_log {K_LOG}\nuseful {useful}\nconst {cpos}\n")
        f.write(f"n_in {n_in}\nn_and {len(ands)}\nn_copy {len(copies)}\nn_assert {len(C.asserts)}\nnnz {nnz}\n")
        f.write(f"terms {k}\nop_bits {nb}\n")
        f.write("c_out " + " ".join(map(str, out_pos)) + "\n")
        f.write(f"rows {useful}\n")
        for kind, a, b in rows:
            f.write(f"{kind} {len(a)} {' '.join(map(str, a))} {len(b)} {' '.join(map(str, b))}\n")
        f.write(f"tests {len(cases)}\n")
        for kind, xs, ws, c, ref in cases:
            f.write(f"{kind} {inbits(xs, ws, c)} {ref:08x}\n")
    summary = dict(pipeline=name, useful=useful, n_in=n_in, n_and=len(ands), n_copy=len(copies),
                   n_assert=len(C.asserts), nnz=nnz, census=cnt, path=path, size=os.path.getsize(path))
    print(summary, flush=True)
    assert len(ands) == cnt["ands"] and useful - 1 == cnt["committed"], (cnt, useful)
    return summary


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    for n in sys.argv[2:] or ["ampere_bf16", "hopper_bf16", "hopper_e4m3"]:
        export(n, outdir)
