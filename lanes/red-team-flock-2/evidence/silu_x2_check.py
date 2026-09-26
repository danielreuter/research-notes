#!/usr/bin/env python3
"""red-team-flock-2: the frame statement's SiLU·mul unit (silu-mul/bf16/element/x2, two elements per unit) against the IR
primitive SiluMulBf16 on adversarial (g, u) pairs, with my own v2 parser and evaluator (rms_check.py); every table entry is
reached through both element slots (u = 1.0).  Usage: silu_x2_check.py NETLIST N [seed]
"""
import random, sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rms_check as R
import diff_ir_units as D


def main():
    netp, N = sys.argv[1], int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 20260926)
    from verity_numerical.bench import templates as TM
    from verity_flock.templates import silu_mul
    from verity_vllm.program.registry import prims as P
    I = 8192
    low = silu_mul.frame_lowering(TM.subcircuit("silu-mul", I=I))
    assert open(netp).read() == low.text
    U = low.units
    nt = R.parse_v2(netp)
    print("STRUCTURE", R.structure(nt))
    icols, ocols = R.port_cols(nt["ig"]), R.port_cols(nt["og"])
    ins0, outs0 = U.in_src[0], [p for k, p in U.out_src[0] if k == "ret"]
    elems = sorted({p % I for _, p in ins0})
    assert len(elems) == 2 and sorted(outs0) == elems, (ins0, outs0)
    cases = [(g, 0x3F80, rng.getrandbits(16), rng.getrandbits(16)) for g in range(1 << 16)]
    cases += [(g, 0x3F80, g ^ 0x8000, 0xBF80) for g in range(1 << 16)]
    while len(cases) < N + (2 << 16):
        a, b = D.silu_case(rng), D.silu_case(rng)
        cases.append((a[0], a[1], b[0], b[1]))
    lanes = len(cases)
    val = {}
    for j, (kind, p) in enumerate(ins0):
        slot = elems.index(p % I)
        role = 0 if p < I else 1
        val[j] = np.array([c[2 * slot + role] for c in cases], dtype=np.uint64)
    z, ok = R.evaluate(nt, [(col, w, val[j]) for j, (col, w) in enumerate(icols)], lanes)
    mism = 0
    for j, (col, w) in enumerate(ocols[:len(outs0)]):
        slot = elems.index(outs0[j])
        got = R.read_port(z, col, w, lanes)
        want = np.array([P.SiluMulBf16.evaluate(c[2 * slot], c[2 * slot + 1]) for c in cases], dtype=np.uint64)
        mism += int((got != want).sum())
    print(f"FIDELITY silu x2: {lanes} units ({2 * lanes} elements), {mism} mismatching outputs, {int((~ok).sum())} unsatisfiable")


if __name__ == "__main__":
    main()
