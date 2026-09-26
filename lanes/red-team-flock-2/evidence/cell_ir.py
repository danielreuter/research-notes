#!/usr/bin/env python3
"""red-team-flock-2: a frame cell's verifier-staged file (flock-ir-frame/v2 or v3, unit-returned outputs) against the IR on
every word: per instance the IR evaluator's outputs and cut-gate values must equal the file's unit-returned output words
(through out_leaf) and cut words, and every unit, evaluated with my own flock-ir-unit/v2 evaluator on the file's own leaves
(through the netlist's leaf map) and cut words, must reproduce its returned words and cut outputs.

  cell_ir.py TEMPLATE PARAMS_JSON INSTANCE_FILE NETLIST
"""
import json, sys, time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rms_check import evaluate, parse_v2, port_cols, read_port  # noqa: E402


def main():
    tpl, params, ipath, netp = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3], sys.argv[4]
    from verity.ir.evaluate import evaluate_call
    from verity_numerical.bench import lowerings, templates as TM
    import verity_flock.ir_lower as IL
    sub = TM.subcircuit(tpl, **params)
    low = lowerings.registry("C-Flock").module(tpl).frame_lowering(sub)
    assert open(netp).read() == low.text, "the netlist is not this lowering"
    U = low.units
    b = open(ipath, "rb").read()
    nl = b.index(b"\n")
    h = json.loads(b[:nl])
    assert h.get("outputs", "units") == "units"
    n, upi = h["instances"], h["units_per_instance"]
    widths = [w for _, w in h["in_ports"]]
    row_words = sum(widths)
    at = nl + 1
    rows = np.frombuffer(b, "<u2", n * row_words, at).reshape(n, row_words).astype(np.uint64); at += 2 * n * row_words
    at += 32 * n * len(widths)
    L = h["layout"]
    rw = L["ret_group"][1]
    outs = np.frombuffer(b, np.uint8, 16 * rw * n * upi, at).reshape(n * upi, 16 * rw); at += 16 * rw * n * upi
    kc = h["cut_words"]
    cuts = np.frombuffer(b, "<u4", n * kc, at).reshape(n, kc).astype(np.uint64) if kc else np.zeros((n, 1), np.uint64)
    at += 4 * n * kc
    assert at == len(b), "file length"
    cols = L["ret_cols"]
    outs = np.concatenate([outs, np.zeros((outs.shape[0], 2), np.uint8)], axis=1)
    ret = np.zeros((n * upi, len(cols)), np.uint64)
    for j, c in enumerate(cols):
        v = outs[:, c // 8].astype(np.uint64) | outs[:, c // 8 + 1].astype(np.uint64) << 8 | outs[:, c // 8 + 2].astype(np.uint64) << 16
        ret[:, j] = (v >> np.uint64(c % 8)) & np.uint64(0xFFFF)
    prog, call = IL.standalone(low.definition)
    t0 = time.time()
    bad_out = bad_cut = 0
    for i in range(n):
        tr = {}
        o = evaluate_call(prog.circuit, call, [int(x) for x in rows[i]], tr)
        if kc and [tr[g] for g in U.cut] != [int(x) for x in cuts[i]]:
            bad_cut += 1
        for u in range(upi):
            want = [o[p] for k, p in U.out_src[u] if k == "ret"]
            if [int(x) for x in ret[i * upi + u, :len(want)]] != want:
                bad_out += 1
                break
    t_ir = time.time() - t0
    nt = parse_v2(netp)
    icols, ocols = port_cols(nt["ig"]), port_cols(nt["og"])
    lanes = n * upi
    assign = []
    for j, (col, w) in enumerate(icols):
        vals = np.zeros(lanes, np.uint64)
        for u in range(upi):
            k, p = U.in_src[u][j]
            vals[u::upi] = rows[:, p] if k == "leaf" else cuts[:, p]
        assign.append((col, w, vals))
    z, ok = evaluate(nt, assign, lanes)
    mism = 0
    r_j = 0
    for j, (col, w) in enumerate(ocols):
        got = read_port(z, col, w, lanes)
        want = np.zeros(lanes, np.uint64)
        for u in range(upi):
            k, p = U.out_src[u][j]
            if k == "ret":
                want[u::upi] = ret[u::upi, [x for x, (kk, _) in enumerate(U.out_src[u]) if kk == "ret"].index(j)]
            else:
                want[u::upi] = cuts[:, p]
        mism += int((got != want).sum())
    print(f"CELL-IR {tpl} {params} {ipath.split('/verifier/')[-1]}: {n} instances; IR vs file: instances with an output word differing "
          f"{bad_out}, with a cut word differing {bad_cut} ({t_ir:.0f} s); units on the file's own leaves and cut words: {lanes} lanes, "
          f"output mismatches {mism}, unsatisfied {int((~ok).sum())}", flush=True)


if __name__ == "__main__":
    main()
