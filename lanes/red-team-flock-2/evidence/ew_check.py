#!/usr/bin/env python3
"""red-team-flock-2: a frame lowering at any parameters (RoPE, SiLU·mul, both RMSNorms) against the IR evaluator on
adversarial rows, with my own flock-ir-unit/v2 parser and bit-sliced evaluator (rms_check.py's), generalising rms_check to
the template's parameters.

Per row the IR evaluator (verity.ir.evaluate.evaluate_call on the Definition) gives the outputs and every cut gate's value;
each unit is evaluated on its leaves (the leaf map, in_src) and cut inputs and must reproduce its returned outputs and cut
outputs bit for bit. My own evaluation of the tail program (IR primitives) must give every cut word no unit computes.

  ew_check.py TEMPLATE PARAMS_JSON NETLIST ROWS [seed]
"""
import hashlib, json, random, sys, time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rms_check import FAMS, evaluate, ir_tail_eval, parse_v2, port_cols, read_port, row, structure  # noqa: E402


def main():
    tpl, params, netp, rows = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20260926
    from verity.ir.evaluate import evaluate_call
    from verity_numerical.bench import lowerings, templates as TM
    from verity_vllm.program.registry import prims as P
    import verity_flock.ir_lower as IL
    rng = random.Random(seed)
    sub = TM.subcircuit(tpl, **params)
    low = lowerings.registry("C-Flock").module(tpl).frame_lowering(sub)
    text = open(netp).read()
    assert text == low.text, "the netlist file is not this lowering"
    print("NETLIST", tpl, params, hashlib.sha256(text.encode()).hexdigest()[:16], flush=True)
    U = low.units
    widths = {p.words for p in sub.inputs}
    assert len(widths) == 1, "ports of different widths"
    N, ports = widths.pop(), len(sub.inputs)
    prog_ir, call = IL.standalone(low.definition)
    cut = list(getattr(U, "cut", None) or [])
    tailp = IL.tail_program(low) if cut else []
    t0 = time.time()
    fams = [FAMS[i % len(FAMS)] for i in range(rows)]
    flat_in, flat_out, cuts, tail_bad = [], [], [], 0
    produced = {k for src in U.out_src for kind, k in src if kind == "cut"}
    for fam in fams:
        r = row(rng, fam, ports, N)
        tr = {}
        outs = evaluate_call(prog_ir.circuit, call, r, tr)
        cw = [tr[g] for g in cut]
        if cut:
            mine = ir_tail_eval(tailp, [cw[k] if k in produced else 0 for k in range(len(cut))], P)
            if any(mine[k] != cw[k] for k in range(len(cut)) if k not in produced):
                tail_bad += 1
        flat_in.append(r); flat_out.append(list(outs)); cuts.append(cw if cut else [0])
    flat_in, flat_out, cuts = (np.array(x, dtype=np.uint64) for x in (flat_in, flat_out, cuts))
    print(f"IR {tpl}: {rows} rows ({ports} ports x {N} words) in {time.time() - t0:.0f} s; {len(cut)} cut words, {len(produced)} "
          f"from units; my tail_program evaluation differs from the IR's cut words on {tail_bad} rows; tail ops "
          f"{sorted({op[1] for op in tailp})}", flush=True)
    nt = parse_v2(netp)
    st = structure(nt)
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
    covered = sorted({p for src in U.out_src for kind, p in src if kind == "ret"})
    bad_rows = sorted({int(l) // U.n for l in np.nonzero(mism | ~ok)[0]})
    print(f"UNITS {tpl} {params}: rows {st['rows']} (structure violations {st['n_bad']}); {lanes} unit lanes ({rows} x {U.n}); "
          f"mismatching {int(mism.sum())}, unsatisfiable {int((~ok).sum())}; returned outputs cover {len(covered)} of {flat_out.shape[1]} "
          f"output words; bad rows {bad_rows[:10]} ({time.time() - t2:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
