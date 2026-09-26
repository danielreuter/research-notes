#!/usr/bin/env python3
"""red-team-flock-2: the RMSNorm warp units (rmsnorm-fused-cuda 9dbeb747, rmsnorm-triton b2155f3f, N = 2048) against the IR
evaluator on adversarial rows, with my own flock-ir-unit/v2 parser and bit-sliced evaluator (not verity_flock's).

Per row the IR evaluator (verity.ir.evaluate.evaluate_call on the template's Definition) gives the outputs and every cut
gate's value; each unit is evaluated on its leaves and cut inputs and must reproduce its outputs and cut outputs bit for bit.
It also checks my own evaluation of `tail_program` (with the IR primitives) against the IR's cut words, and writes the rows
as instance files (the IR's cut words and outputs) so the Rust verifier's load-time check (`check_cuts`, `ir_tail`) meets
them: a refusal there is the Rust tail disagreeing with the IR evaluator.

  rms_check.py TEMPLATE NETLIST ROWS OUTDIR [seed] [--no-units]
"""
import hashlib, json, random, sys, time

import numpy as np

WORD = 128


def parse_v2(path):
    lines = open(path).read().splitlines()
    h = lines[0].split()
    assert h[0] == "flock-ir-unit/v2"
    n = lambda i: int(h[i])
    useful, const = n(2), n(3)
    at = 4

    def groups():
        nonlocal at
        c = n(at); at += 1
        out = []
        for _ in range(c):
            col, words, np_ = n(at), n(at + 1), n(at + 2)
            out.append((col, words, [n(at + 3 + i) for i in range(np_)]))
            at += 3 + np_
        return out
    ig, og = groups(), groups()
    A, B = [], []
    for ln in lines[1:1 + useful]:
        v = ln.split()
        na = int(v[0])
        A.append(np.array(v[1:1 + na], dtype=np.int64)); B.append(np.array(v[2 + na:], dtype=np.int64))
    return dict(useful=useful, const=const, ig=ig, og=og, A=A, B=B)


def port_cols(groups):
    cols = []
    for col, words, bits in groups:
        at = col * WORD
        for b in bits:
            cols.append((at, b)); at += b
        assert at <= (col + words) * WORD
    return cols


def tiling(groups):
    """Groups tile [first col, last col + words) with no gap and no overlap."""
    spans = sorted((c, c + w) for c, w, _ in groups)
    return all(spans[i][1] == spans[i + 1][0] for i in range(len(spans) - 1)), spans


def structure(nt):
    A, B, c = nt["A"], nt["B"], nt["const"]
    in_words = max(c0 + w for c0, w, _ in nt["ig"])
    first = in_words * WORD
    inputs = set()
    for col, b in port_cols(nt["ig"]):
        inputs.update(range(col, col + b))
    bad = []
    for i in range(nt["useful"]):
        a, b = A[i].tolist(), B[i].tolist()
        if i < first:
            ok = (a == [i] and b == [i]) if i in inputs else (a == [] and b == [])
        elif i == c:
            ok = a == [c] and b == [c]
        else:
            ok = all(x < i or x == c or (x == i and b == [c]) for x in a + b) and not (a == [i] and b == [i])
        if not ok:
            bad.append(i)
    return {"rows": nt["useful"], "n_bad": len(bad), "bad": bad[:5], "in_tiling": tiling(nt["ig"]), "out_tiling": tiling(nt["og"])}


def evaluate(nt, in_assign, lanes):
    """in_assign: list of (first column, width, values (lanes,) uint64). Returns z (rows, W) and the satisfied-lane mask."""
    W = (lanes + 63) // 64
    z = np.zeros((nt["useful"], W), dtype=np.uint64)
    li = np.arange(lanes)
    sh = (li % 64).astype(np.uint64)
    for col, w, vals in in_assign:
        vals = np.asarray(vals, dtype=np.uint64)
        for b in range(w):
            bits = (vals >> np.uint64(b)) & np.uint64(1)
            wv = np.zeros(W, dtype=np.uint64)
            np.bitwise_or.at(wv, li // 64, bits << sh)
            z[col + b] = wv
    full = np.uint64(0xFFFFFFFFFFFFFFFF)
    z[nt["const"]] = full
    zero = np.zeros(W, dtype=np.uint64)
    xr = lambda idx: np.bitwise_xor.reduce(z[idx], axis=0) if len(idx) else zero
    A, B, c = nt["A"], nt["B"], nt["const"]
    first = max(c0 + w for c0, w, _ in nt["ig"]) * WORD
    for i in range(first, nt["useful"]):
        if i == c:
            continue
        a = A[i][A[i] != i]
        z[i] = xr(a) & xr(B[i])
    ok = np.full(W, full)
    for i in range(nt["useful"]):
        ok &= ~((xr(A[i]) & xr(B[i])) ^ z[i])
    okl = ((ok[li // 64] >> sh) & np.uint64(1)).astype(bool)
    return z, okl


def read_port(z, col, w, lanes):
    li = np.arange(lanes)
    sh = (li % 64).astype(np.uint64)
    out = np.zeros(lanes, dtype=np.uint64)
    for b in range(w):
        out |= ((z[col + b][li // 64] >> sh) & np.uint64(1)) << np.uint64(b)
    return out


def bf(rng, fam):
    s = rng.getrandbits(1) << 15
    if fam == "any":
        return rng.getrandbits(16)
    if fam == "huge":
        return s | (rng.randrange(0xC0, 0xFF) << 7) | rng.getrandbits(7)
    if fam == "tiny":
        return s | (rng.randrange(1, 0x30) << 7) | rng.getrandbits(7)
    if fam == "sub":
        return s | rng.randrange(0, 0x80)
    if fam == "near":
        return s | (rng.randrange(0x72, 0x7A) << 7) | rng.getrandbits(7)    # |x| ~ 2^-13 .. 2^-6: mean square ~ eps
    if fam == "wide":
        return s | (rng.randrange(1, 0xFF) << 7) | rng.getrandbits(7)
    return s | (rng.randrange(0x70, 0x88) << 7) | rng.getrandbits(7)


FAMS = ["normal", "wide", "huge", "tiny", "sub", "one_nan", "one_inf", "cancel", "zero", "mixed", "any", "w_special", "near_eps"]


def row(rng, fam, ports, N):
    base = {"one_nan": "normal", "one_inf": "normal", "cancel": "normal", "zero": "normal", "w_special": "normal"}.get(fam, fam)
    if fam == "near_eps":
        vals = [[bf(rng, "near") for _ in range(N)] for _ in range(ports - 1)] + [[bf(rng, "normal") for _ in range(N)]]
    elif fam == "mixed":
        vals = [[bf(rng, rng.choice(["huge", "tiny", "normal", "sub"])) for _ in range(N)] for _ in range(ports)]
    else:
        vals = [[bf(rng, base) for _ in range(N)] for _ in range(ports)]
    if fam == "one_nan":
        vals[0][rng.randrange(N)] = 0x7FC0 | rng.randrange(0, 0x40)
    if fam == "one_inf":
        vals[0][rng.randrange(N)] = rng.choice([0x7F80, 0xFF80])
    if fam == "zero":
        vals[0] = [rng.choice([0, 0x8000]) for _ in range(N)]
        if ports == 3:
            vals[1] = [rng.choice([0, 0x8000]) for _ in range(N)]
    if fam == "cancel" and ports == 3:
        vals[1] = [v ^ 0x8000 for v in vals[0]]               # res = -x: the residual sum is exactly zero
    if fam == "w_special":
        vals[-1] = [rng.choice([0, 0x8000, 0x7F80, 0x7FC0, 0x0001, 0x3F80]) for _ in range(N)]
    return [v for p in vals for v in p]


def ir_tail_eval(prog, cut_vals, P):
    """My own evaluation of the tail program with the IR primitives (verity_vllm .evaluate)."""
    slots = dict(enumerate(cut_vals))
    fn = {"F32Add_v1": P.F32Add, "F32Mul_v1": P.F32Mul, "F32Fma_v1": P.F32Fma, "F32Div_v1": P.F32Div, "RsqrtApprox_v1": P.RsqrtApprox,
          "MufuSqrtFtz_v1": P.MufuSqrtFtz, "DivFullRcp_v1": P.DivFullRcp, "DivFullScaleA_v1": P.DivFullScaleA}
    for op in prog:
        out, pid = op[0], op[1]
        slots[out] = op[2] if pid == "Const" else fn[pid].evaluate(*[slots[a] for a in op[2:]])
    return slots


def main():
    tpl, netp, rows, outdir = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    seed = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 20260926
    do_units = "--no-units" not in sys.argv
    from verity.ir.evaluate import evaluate_call
    from verity_numerical.bench import lowerings, templates as TM
    from verity_vllm.program.registry import prims as P
    import verity_flock.ir_lower as IL
    rng = random.Random(seed)
    N = 2048
    sub = TM.subcircuit(tpl, N=N, EPS=1e-5)
    low = lowerings.registry("C-Flock").module(tpl).lowering(sub)
    text = open(netp).read()
    assert text == low.text, "the netlist file is not this lowering"
    print("NETLIST", tpl, hashlib.sha256(text.encode()).hexdigest()[:16], flush=True)
    U = low.units
    prog_ir, call = IL.standalone(low.definition)
    tailp = IL.tail_program(low)
    ports = len(sub.inputs)
    t0 = time.time()
    fams = [FAMS[i % len(FAMS)] for i in range(rows)]
    flat_in, flat_out, cuts, tail_bad = [], [], [], 0
    for fam in fams:
        r = row(rng, fam, ports, N)
        tr = {}
        outs = evaluate_call(prog_ir.circuit, call, r, tr)
        cw = [tr[g] for g in U.cut]
        # the tail's outputs (the cut words no unit computes) from the units' cut words alone
        produced = {k for src in U.out_src for kind, k in src if kind == "cut"}
        seed_vals = [tr[U.cut[k]] if k in produced else 0 for k in range(len(U.cut))]
        mine = ir_tail_eval(tailp, seed_vals, P)
        if any(mine[k] != cw[k] for k in range(len(U.cut)) if k not in produced):
            tail_bad += 1
        flat_in.append(r); flat_out.append(list(outs)); cuts.append(cw)
    flat_in, flat_out, cuts = (np.array(x, dtype=np.uint64) for x in (flat_in, flat_out, cuts))
    print(f"IR {tpl}: {rows} rows evaluated in {time.time() - t0:.0f} s; my tail_program evaluation (IR primitives) differs "
          f"from the IR's cut words on {tail_bad} rows", flush=True)
    fam_count = {f: fams.count(f) for f in FAMS}
    zero_scalar = int(sum(1 for c in cuts[:, -1].tolist() if c in (0, 0x80000000)))
    nan_scalar = int(sum(1 for c in cuts[:, -1].tolist() if (c & 0x7F800000) == 0x7F800000 and c & 0x7FFFFF))
    inf_scalar = int(sum(1 for c in cuts[:, -1].tolist() if (c & 0x7FFFFFFF) == 0x7F800000))
    print("SCALARS", json.dumps({"families": fam_count, "zero": zero_scalar, "nan": nan_scalar, "inf": inf_scalar}), flush=True)
    path = f"{outdir}/inst-{tpl}-adv-{rows}.bin"
    IL.write_instances(low, flat_in, flat_out, path, {"set": "red-team-flock-2/rms-adversarial", "subcircuit": sub.id,
                                                      "range": [0, rows], "seed": seed}, cuts)
    print("WROTE", path, flush=True)
    if not do_units:
        return
    t1 = time.time()
    nt = parse_v2(netp)
    print("STRUCTURE", json.dumps(structure(nt)), f"{time.time() - t1:.0f} s", flush=True)
    icols, ocols = port_cols(nt["ig"]), port_cols(nt["og"])
    assert [c for c, _ in icols] == list(low.layout.in_port_cols), "my input port columns differ from the layout's"
    lanes = rows * U.n
    assign = []
    for j, (col, w) in enumerate(icols):
        vals = np.zeros(lanes, dtype=np.uint64)
        for u in range(U.n):
            kind, p = U.in_src[u][j]
            vals[u::U.n] = flat_in[:, p] if kind == "leaf" else cuts[:, p]
        assign.append((col, w, vals))
    t2 = time.time()
    z, ok = evaluate(nt, assign, lanes)
    mism = np.zeros(lanes, dtype=bool)
    for j, (col, w) in enumerate(ocols):
        got = read_port(z, col, w, lanes)
        want = np.zeros(lanes, dtype=np.uint64)
        for u in range(U.n):
            kind, p = U.out_src[u][j]
            want[u::U.n] = flat_out[:, p] if kind == "ret" else cuts[:, p]
        mism |= got != want
    bad_rows = sorted({int(l) // U.n for l in np.nonzero(mism | ~ok)[0]})
    print(f"UNITS {tpl}: {lanes} unit lanes ({rows} rows x {U.n}), {int(mism.sum())} mismatching lanes, {int((~ok).sum())} "
          f"unsatisfiable, {time.time() - t2:.0f} s; bad rows {bad_rows[:10]} families {[fams[r] for r in bad_rows[:10]]}", flush=True)


if __name__ == "__main__":
    main()
