#!/usr/bin/env python3
"""red-team-flock-2: tampered cut accounting for a staged flock-ir-instances/v1 RMSNorm file (header edits the verifier's
load checks must refuse), and one consistent forgery: the tail's eps constant changed, the row scalar recomputed from it
(the IR primitives) and every unit's outputs recomputed with it (my evaluator, rms_check.py), so the file is internally
consistent but is not the template's (IR4: does the Rust verifier pin the tail it evaluates?).

  cut_tamper.py STAGED_FILE NETLIST OUTDIR
"""
import copy, json, sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rms_check as R

WORD = 128


def load(p):
    b = open(p, "rb").read()
    nl = b.index(b"\n")
    return json.loads(b[:nl]), b[nl + 1:]


def save(p, h, body):
    with open(p, "wb") as f:
        f.write(json.dumps(h, sort_keys=True).encode() + b"\n")
        f.write(body)


def header_tampers(h):
    c = h["cut"]
    T = {}
    t = copy.deepcopy(h); t["cut"]["tail"][0], t["cut"]["tail"][1] = t["cut"]["tail"][1], t["cut"]["tail"][0]; T["tail_reordered"] = t
    t = copy.deepcopy(h); t["cut"]["tail"][-1][0] = 0; T["tail_writes_unit_word"] = t
    t = copy.deepcopy(h); t["cut"]["out"][1] = copy.deepcopy(c["out"][0]); T["two_units_one_word"] = t
    t = copy.deepcopy(h); t["cut"]["tail"] = t["cut"]["tail"][:-1]; T["tail_truncated"] = t
    t = copy.deepcopy(h); t["cut"]["in"][0] = [[c["in"][0][0][0] - 32, c["in"][0][0][1]]]; T["cut_port_col_moved"] = t
    t = copy.deepcopy(h); t["instances"] = h["instances"] + 1; T["instances_mismatch"] = t
    t = copy.deepcopy(h); t["cut_words"] = h["cut_words"] + 1; t["cut"]["words"] = h["cut_words"] + 1; T["extra_cut_word"] = t
    t = copy.deepcopy(h); t["cut"]["in"][0] = [[c["in"][0][0][0], 1]]; T["unit_reads_other_units_aggregate"] = t
    t = copy.deepcopy(h); t["cut"]["tail"][-1][1] = "F32Sqrt_v1"; T["tail_unknown_primitive"] = t
    t = copy.deepcopy(h); op = t["cut"]["tail"][-2]; op[2] = op[0]; T["tail_op_reads_itself"] = t
    return T


def forge_eps(h, body, netp, eps_word=0x3A83126F):
    from verity_vllm.program.registry import prims as P
    nt = R.parse_v2(netp)
    upi, units, iw, ow = h["units_per_instance"], h["units"], h["in_words"], h["out_words"]
    n = units // upi
    ib = np.frombuffer(body[:units * iw * 16], dtype=np.uint8).reshape(units, iw * 16)
    ins = np.unpackbits(ib, axis=1, bitorder="little").astype(np.uint64)
    ob = np.frombuffer(body[units * iw * 16:], dtype=np.uint8).reshape(units, ow * 16)
    outs = np.unpackbits(ob, axis=1, bitorder="little").astype(np.uint64)
    o0 = min(c for c, _, _ in nt["og"])
    word32 = lambda bits, col: int(sum(int(bits[col + b]) << b for b in range(32)))
    tail = copy.deepcopy(h["cut"]["tail"])
    k = [i for i, op in enumerate(tail) if op[1] == "Const" and op[2] == 925353388]
    assert len(k) == 1, "the eps constant 1e-5 not found once in the tail"
    tail[k[0]][2] = eps_word
    cut_in = [(c, w) for c, w in [tuple(p) for p in h["cut"]["in"][0]]]
    for i in range(n):
        agg = [0] * h["cut_words"]
        for u in range(upi):
            for col, kw in h["cut"]["out"][u]:
                agg[kw] = word32(outs[i * upi + u], col)
        slots = R.ir_tail_eval(tail, agg, P)
        for u in range(upi):
            for col, kw in h["cut"]["in"][u]:
                v = slots[kw]
                for b in range(32):
                    ins[i * upi + u, col + b] = (v >> b) & 1
    assign = [(col, w, sum(ins[:, col + b] << np.uint64(b) for b in range(w))) for col, w in R.port_cols(nt["ig"])]
    z, ok = R.evaluate(nt, assign, units)
    assert ok.all(), "the forged file's units are unsatisfiable"
    li = np.arange(units)
    sh = (li % 64).astype(np.uint64)
    newout = np.zeros((units, ow * WORD), dtype=np.uint8)
    for j in range(ow * WORD):
        newout[:, j] = ((z[o0 * WORD + j][li // 64] >> sh) & np.uint64(1)).astype(np.uint8)
    nh = copy.deepcopy(h)
    nh["cut"]["tail"] = tail
    nb = np.packbits(ins.astype(np.uint8), axis=1, bitorder="little").tobytes() + np.packbits(newout, axis=1, bitorder="little").tobytes()
    changed = int((newout != outs.astype(np.uint8)).any(axis=1).sum())
    return nh, nb, changed


def main():
    src, netp, out = sys.argv[1:4]
    h, body = load(src)
    for name, t in header_tampers(h).items():
        save(f"{out}/t-{name}.bin", t, body)
        print("WROTE", name)
    nh, nb, changed = forge_eps(h, body, netp)
    save(f"{out}/t-eps_forged_consistent.bin", nh, nb)
    print(f"WROTE eps_forged_consistent: {changed} of {h['units']} units' outputs changed with eps = 1e-3")


if __name__ == "__main__":
    main()
