"""flock-bench: export the binary-census unit circuit (gf2.py/unit.py, copied from the survey agent's
internal/binary-census) as one Flock block-R1CS base block, C = I: row i is (A_i . z)(B_i . z) = z_i.

Column layout (one unit): inputs x, w, c (A = B = {i}); live ANDs in creation order (A, B = the two forms);
one row per assertion L = 0, encoded (L + z_j) * 1 = z_j; one copy row per output bit that is not already a
single committed bit ((f) * 1 = z_j); the constant-one wire last (A = B = {const}, pinned by Flock).
A form's constant term is the constant column.

Output (text): header "useful const n_in n_x n_w n_c"; `useful` lines "na a... nb b..."; then NV test vectors,
each "inputs_hex z_hex" (LSB-first bit strings as little-endian hex), all rows checked here before writing.

usage: python3 export_unit.py ampere_bf16|hopper_bf16|ada_e4m3|hopper_e4m3 OUT [NV]
"""
from __future__ import annotations

import random
import sys
import time

import unit as U

PIPES = {
    "ampere_bf16": (U.BF16, (8, 8), 25, -132),
    "hopper_bf16": (U.BF16, (16,), 26, -133),
    "ada_e4m3": (U.E4M3, (16, 16), 14, -139),
    "hopper_e4m3": (U.E4M3, (32,), 14, -139),
}


def rand_bf16(rng):
    s = rng.getrandbits(1)
    r = rng.random()
    if r < 0.30:
        e = rng.randint(120, 134)
    elif r < 0.45:
        e = rng.randint(0, 254)
    elif r < 0.55:
        e = 0
    elif r < 0.70:
        e = rng.randint(1, 12)
    else:
        e = rng.randint(100, 150)
    m = rng.getrandbits(7) if rng.random() > 0.08 else 0
    return (s << 15) | (e << 7) | m


def rand_e4m3(rng):
    while True:
        w = rng.getrandbits(8)
        if (w & 0x7F) != 0x7F:
            return w


def rand_acc(rng):
    s = rng.getrandbits(1)
    e = rng.randint(100, 150) if rng.random() < 0.8 else 0
    return (s << 31) | (e << 23) | rng.getrandbits(23)


def main():
    name, out = sys.argv[1], sys.argv[2]
    nv = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    fmt, groups, W, F = PIPES[name]
    t0 = time.time()
    C = U.unit(fmt, groups, W, F)
    cnt = C.counts()
    live = C.live()
    ins = [w for nm in ("x", "w", "c") for w in C.inputs[nm]]
    in_idx = [next(iter(w.s)) for w in ins]
    col = {}
    for v in in_idx:
        col[v] = len(col)
    ands = [v for v in range(len(C.kind)) if v in live and C.kind[v] == "and"]
    for v in ands:
        col[v] = len(col)
    assert all(C.kind[v] in ("in", "and") for v in live), "hints not supported"
    rows_a, rows_b, kinds = [], [], []
    CONST = None  # patched below

    def form(L):
        s = [col[v] for v in L.s]
        if L.c:
            s.append("C")
        return s

    for v in in_idx:
        rows_a.append([col[v]]); rows_b.append([col[v]]); kinds.append("in")
    for v in ands:
        a, b = C.data[v]
        rows_a.append(form(a)); rows_b.append(form(b)); kinds.append("and")
    for _, L in C.asserts:
        j = len(rows_a)
        rows_a.append(form(L) + [j]); rows_b.append(["C"]); kinds.append("assert")
    cout = []  # flock-glue: committed column of each c_out bit (for chaining units on the device)
    for nm, bits in C.outputs.items():
        for w in bits:
            if len(w.s) == 1 and w.c == 0:
                if nm == "c_out":
                    cout.append(col[next(iter(w.s))])
                continue
            if nm == "c_out":
                cout.append(len(rows_a))
            rows_a.append(form(w)); rows_b.append(["C"]); kinds.append("copy")
    CONST = len(rows_a)
    rows_a.append([CONST]); rows_b.append([CONST]); kinds.append("const")
    useful = len(rows_a)

    def fix(r):
        out = {}
        for c in r:
            c = CONST if c == "C" else c
            out[c] = out.get(c, 0) ^ 1
        return sorted(c for c, p in out.items() if p)

    rows_a = [fix(r) for r in rows_a]
    rows_b = [fix(r) for r in rows_b]
    assert useful <= 8192, useful

    rng = random.Random(20260925)
    k = sum(groups)
    rop = rand_bf16 if fmt is U.BF16 else rand_e4m3
    vecs = []
    for _ in range(nv):
        xs = [rop(rng) for _ in range(k)]
        ws = [rop(rng) for _ in range(k)]
        c = rand_acc(rng)
        bits = []
        for arr in (xs, ws):
            for v in arr:
                bits += [(v >> i) & 1 for i in range(fmt.bits)]
        bits += [(c >> i) & 1 for i in range(32)]
        vecs.append(bits)
    n_in = len(in_idx)
    assert all(len(b) == n_in for b in vecs)
    # bit-sliced evaluation of every row, then check (A z)(B z) = z row by row
    T = nv
    mask = (1 << T) - 1
    z = [0] * useful
    for i in range(n_in):
        z[i] = sum(vecs[t][i] << t for t in range(T))
    z[CONST] = mask

    def ev(r):
        x = 0
        for c in r:
            x ^= z[c]
        return x

    for i in range(n_in, useful):
        if kinds[i] == "const":
            continue
        z[i] = ev(rows_a[i]) & ev(rows_b[i])
    bad = 0
    for i in range(useful):
        if (ev(rows_a[i]) & ev(rows_b[i])) != z[i]:
            bad += 1
    fails = 0
    for _, L in C.asserts:
        fails |= ev(fix(form(L)))
    assert bad == 0 and fails == 0, (bad, bin(fails).count("1"))
    nnz = sum(len(r) for r in rows_a) + sum(len(r) for r in rows_b)
    with open(out, "w") as f:
        f.write(f"{useful} {CONST} {n_in} {len(C.inputs['x'])} {len(C.inputs['w'])} {len(C.inputs['c'])}\n")
        for ra, rb in zip(rows_a, rows_b):
            f.write(f"{len(ra)} {' '.join(map(str, ra))} {len(rb)} {' '.join(map(str, rb))}\n")
        f.write(f"{T}\n")
        for t in range(T):
            ib = bytearray((n_in + 7) // 8)
            zb = bytearray((useful + 7) // 8)
            for i in range(n_in):
                if vecs[t][i]:
                    ib[i >> 3] |= 1 << (i & 7)
            for i in range(useful):
                if z[i] >> t & 1:
                    zb[i >> 3] |= 1 << (i & 7)
            f.write(f"{ib.hex()} {zb.hex()}\n")
        assert len(cout) == 32 and len(C.inputs["c"]) == 32
        f.write("COUT " + " ".join(map(str, cout)) + "\n")
    kc = {kk: kinds.count(kk) for kk in ("in", "and", "assert", "copy", "const")}
    print(f"EXPORT\t{name}\tuseful={useful}\tconst={CONST}\tkinds={kc}\tnnz_AB={nnz}\tcensus={cnt}\t"
          f"vectors={T}\trows_ok\tsecs={time.time() - t0:.1f}", flush=True)


if __name__ == "__main__":
    main()
