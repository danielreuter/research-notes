#!/usr/bin/env python3
"""red-team-flock-2: the pinned flock-ir-unit/v1 netlists (rope-head/neox-bf16/pair 25d8e464, silu-mul/bf16/element 5bb4a943)
against the IR primitives (verity_vllm RopeOut / RopeOutAdd / SiluMulBf16 .evaluate), with my own netlist parser and
bit-sliced evaluator (nothing from verity_flock).

1. Structure: input rows A = B = [i], unused input/output rows empty, the constant row last; every other row references only
   earlier columns or the constant, except assertion rows (A = L + [i], B = [const]), whose own column no row reads; no free
   row; the output columns are copy rows.
2. Fidelity: every row satisfied and the output words equal to the primitive on adversarial families.

  diff_ir_units.py rope NETLIST N [seed]  |  diff_ir_units.py silu NETLIST N [seed]
"""
import random, sys, time

import numpy as np

WORD = 128


def parse(path):
    lines = open(path).read().splitlines()
    h = lines[0].split()
    n = lambda i: int(h[i])
    useful, const, in_words, n_in = n(2), n(3), n(4), n(5)
    in_bits = [n(6 + i) for i in range(n_in)]
    out_col, out_words, n_out = n(6 + n_in), n(7 + n_in), n(8 + n_in)
    out_bits = [n(9 + n_in + i) for i in range(n_out)]
    A, B = [], []
    for ln in lines[1:1 + useful]:
        v = list(map(int, ln.split()))
        na = v[0]
        A.append(v[1:1 + na]); B.append(v[2 + na:2 + na + v[1 + na]])
    assert len(A) == useful and const == useful - 1
    return dict(useful=useful, const=const, in_words=in_words, in_bits=in_bits, out_col=out_col, out_words=out_words,
                out_bits=out_bits, A=A, B=B)


def structure(nt):
    A, B, c = nt["A"], nt["B"], nt["const"]
    used, first = sum(nt["in_bits"]), nt["in_words"] * WORD
    o0, o1 = nt["out_col"] * WORD, (nt["out_col"] + nt["out_words"]) * WORD
    uo = sum(nt["out_bits"])
    bad, asserts, readers = [], [], set()
    for i in range(nt["useful"]):
        a, b = A[i], B[i]
        if i < used:
            ok = a == [i] and b == [i]
        elif i < first:
            ok = a == [] and b == []
        elif i == c:
            ok = a == [c] and b == [c]
        elif o0 + uo <= i < o1:
            ok = a == [] and b == []
        elif o0 <= i < o0 + uo:
            ok = b == [c] and all(x < i for x in a)
        elif i in a and b == [c]:
            asserts.append(i); ok = all(x < i or x == i for x in a)
        else:
            ok = all(x < i or x == c for x in a + b) and not (a == [i] and b == [i])
        if not ok:
            bad.append(i)
        if i >= first:
            readers.update(x for x in a + b if x != i)
    read_asserts = [j for j in asserts if j in readers]
    read_outputs = [j for j in range(o0, o1) if j in readers]
    return {"rows": nt["useful"], "bad_rows": bad[:10], "n_bad": len(bad), "assert_rows": len(asserts),
            "assert_rows_read": read_asserts[:5], "output_rows_read": read_outputs[:5], "out_rows": [o0, o0 + uo]}


def evaluate(nt, inputs):
    """inputs: (N,) uint64 input word value (<= 64 used bits). Returns (out (N, out_words*128 bits as python ints), ok mask)."""
    N = len(inputs)
    W = (N + 63) // 64
    rows = nt["useful"]
    z = np.zeros((rows, W), dtype=np.uint64)
    used = sum(nt["in_bits"])
    lanes = np.arange(N)
    for b in range(used):
        bits = ((inputs >> np.uint64(b)) & np.uint64(1)).astype(np.uint64)
        wv = np.zeros(W, dtype=np.uint64)
        np.bitwise_or.at(wv, lanes // 64, bits << (lanes % 64).astype(np.uint64))
        z[b] = wv
    full = np.uint64(0xFFFFFFFFFFFFFFFF)
    z[nt["const"]] = full
    A, B = nt["A"], nt["B"]
    xr = lambda idx: np.bitwise_xor.reduce(z[idx], axis=0) if idx else np.zeros(W, dtype=np.uint64)
    for i in range(nt["in_words"] * WORD, rows):
        if i == nt["const"]:
            continue
        a = [x for x in A[i] if x != i]
        z[i] = xr(a) & xr(B[i])
    ok = np.full(W, full)
    for i in range(rows):
        ok &= ~((xr(A[i]) & xr(B[i])) ^ z[i])
    o0 = nt["out_col"] * WORD
    uo = sum(nt["out_bits"])
    out = np.zeros(N, dtype=np.uint64)
    for t in range(uo):
        bits = (z[o0 + t][lanes // 64] >> (lanes % 64).astype(np.uint64)) & np.uint64(1)
        out |= bits << np.uint64(t)
    okl = ((ok[lanes // 64] >> (lanes % 64).astype(np.uint64)) & np.uint64(1)).astype(bool)
    return out, okl


def bf(rng, fam):
    s = rng.getrandbits(1) << 15
    if fam == "any":
        return rng.getrandbits(16)
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 0x80)
    if fam == "inf":
        return s | 0x7F80
    if fam == "nan":
        return s | 0x7F80 | rng.randrange(1, 0x80)
    if fam == "big":
        return s | (rng.randrange(0xF0, 0xFF) << 7) | rng.getrandbits(7)
    if fam == "tiny":
        return s | (rng.randrange(1, 0x12) << 7) | rng.getrandbits(7)
    return s | (rng.randrange(1, 0xFF) << 7) | rng.getrandbits(7)


def with_exp(v, e):
    return (v & 0x807F) | (max(1, min(0xFE, e)) << 7)


def rope_case(rng):
    k = rng.randrange(12)
    fams = ["norm", "norm", "any", "sub", "zero", "inf", "nan", "big", "tiny"]
    x, y, c, s = (bf(rng, rng.choice(fams)) for _ in range(4))
    if k == 0:                               # exact cancellation in one output, doubling in the other
        y, s = x, c
    elif k == 1:
        y, s = x, c ^ 0x8000
    elif k == 2:                             # near cancellation: one operand off by a few ulps
        y, s = x, (c & 0xFF80) | ((c + rng.choice([1, 2, 3, -1, -2])) & 0x7F)
    elif k == 3:                             # the addend at a chosen exponent gap (the fma window, the clamp and the sticky)
        x, c, y, s = (bf(rng, "norm") for _ in range(4))
        ep = ((x >> 7) & 0xFF) + ((c >> 7) & 0xFF)
        gap = rng.randrange(-45, 46)
        es = ep - gap - ((y >> 7) & 0xFF)
        s = with_exp(s, es)
    elif k == 4:                             # products near underflow
        x, c = with_exp(x, rng.randrange(1, 40)), with_exp(c, rng.randrange(80, 110))
        y, s = with_exp(y, rng.randrange(1, 40)), with_exp(s, rng.randrange(80, 110))
    elif k == 5:                             # products near overflow
        x, c = with_exp(x, rng.randrange(120, 140)), with_exp(c, rng.randrange(120, 140))
        y, s = with_exp(y, rng.randrange(120, 140)), with_exp(s, rng.randrange(120, 140))
    elif k == 6:                             # single rounding (the second product zero): bf16 ties of a 16-bit product
        s = rng.choice([0, 0x8000])
    elif k == 7:                             # bf16 subnormal operands
        x, y = bf(rng, "sub"), bf(rng, "sub")
    return x, y, c, s


def silu_case(rng):
    k = rng.randrange(8)
    fams = ["norm", "norm", "any", "sub", "zero", "inf", "nan", "big", "tiny"]
    g, u = bf(rng, rng.choice(fams)), bf(rng, rng.choice(fams))
    if k == 0:
        u = rng.choice([0x3F80, 0xBF80, 0x0001, 0x8001, 0x7F7F, 0x0080])
    elif k == 1:
        g = with_exp(g, rng.randrange(0x70, 0x88))        # silu's interesting range |g| ~ 2^-15 .. 2^8
    elif k == 2:
        u = with_exp(u, rng.randrange(0xF0, 0xFF))        # overflow of s * u
    elif k == 3:
        u = with_exp(u, rng.randrange(1, 0x10))           # underflow of s * u
    return g, u


def main():
    which, path, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 20260926)
    from verity_vllm.program.registry import prims as P
    nt = parse(path)
    print("STRUCTURE", structure(nt), flush=True)
    t0 = time.time()
    total = mism = unsat = 0
    first = []
    batches = []
    if which == "silu":
        batches.append([(g, 0x3F80) for g in range(1 << 16)])            # every table entry, u = 1.0
        batches.append([(g, 0xBF80) for g in range(1 << 16)])            # u = -1.0
    B = 1 << 15
    while sum(len(b) for b in batches) < N + (2 << 16 if which == "silu" else 0):
        batches.append([rope_case(rng) if which == "rope" else silu_case(rng) for _ in range(B)])
    for cases in batches:
        if which == "rope":
            inp = np.array([x | (y << 16) | (c << 32) | (s << 48) for x, y, c, s in cases], dtype=np.uint64)
            want = [P.RopeOut.evaluate(x, y, c, s) | (P.RopeOutAdd.evaluate(x, y, c, s) << 16) for x, y, c, s in cases]
        else:
            inp = np.array([g | (u << 16) for g, u in cases], dtype=np.uint64)
            want = [P.SiluMulBf16.evaluate(g, u) for g, u in cases]
        got, ok = evaluate(nt, inp)
        for i, (w, gv, o) in enumerate(zip(want, got.tolist(), ok.tolist())):
            total += 1
            if not o:
                unsat += 1
                if len(first) < 8:
                    first.append(("UNSAT", [hex(v) for v in cases[i]], hex(w)))
            elif w != gv:
                mism += 1
                if len(first) < 8:
                    first.append(("MISMATCH", [hex(v) for v in cases[i]], hex(w), hex(gv)))
    print(f"FIDELITY {which}: {total} units, {mism} mismatches, {unsat} unsatisfiable, {time.time() - t0:.0f} s", flush=True)
    for f in first:
        print("  ", f)


if __name__ == "__main__":
    main()
