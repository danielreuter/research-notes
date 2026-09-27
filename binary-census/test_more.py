"""Targeted distributions for the unit circuit, a 96-step chain test on the 24 real captured VUs, and the negatives."""
from __future__ import annotations

import glob
import json
import os
import random
import struct
import sys

sys.path.insert(0, "/workspace/packages/verity/src")
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

from verity.ml.tc.cast import f32_to_bf16_word  # noqa: E402
from verity.ml.tc.models import AMPERE_BF16_M16N8K16, HOPPER_BF16_M16N8K16  # noqa: E402

import unit as U  # noqa: E402


def slice_inputs(cases, k, nb):
    xin = [0] * (k * nb)
    win = [0] * (k * nb)
    cin = [0] * 32
    for t, (xs, ws, c) in enumerate(cases):
        for i in range(k):
            for b in range(nb):
                if xs[i] >> b & 1:
                    xin[i * nb + b] |= 1 << t
                if ws[i] >> b & 1:
                    win[i * nb + b] |= 1 << t
        for b in range(32):
            if c >> b & 1:
                cin[b] |= 1 << t
    return {"x": xin, "w": win, "c": cin}


def unslice(bits, T):
    out = [0] * T
    for b, v in enumerate(bits):
        for t in range(T):
            if v >> t & 1:
                out[t] |= 1 << b
    return out


def classify(word):
    e = (word >> 23) & 0xFF
    m = word & 0x7FFFFF
    if e == 0xFF:
        return "inf"
    if e == 0:
        return "zero" if m == 0 else "subnormal"
    return "normal"


def bf16(s, e, m):
    return (s << 15) | (e << 7) | m


def targeted(rng, family):
    k = 16
    if family == "realistic":
        xs = [bf16(rng.getrandbits(1), rng.randint(118, 130), rng.getrandbits(7)) for _ in range(k)]
        ws = [bf16(rng.getrandbits(1), rng.randint(110, 126), rng.getrandbits(7)) for _ in range(k)]
        c = (rng.getrandbits(1) << 31) | (rng.randint(110, 135) << 23) | rng.getrandbits(23)
    elif family == "exact_cancel":
        xs, ws = [], []
        for _ in range(k // 2):
            a = bf16(rng.getrandbits(1), rng.randint(100, 150), rng.getrandbits(7))
            b = bf16(rng.getrandbits(1), rng.randint(100, 150), rng.getrandbits(7))
            xs += [a, a ^ 0x8000]
            ws += [b, b]
        c = 0 if rng.random() < 0.5 else 0x80000000
    elif family == "tiny_subnormal_results":
        xs = [bf16(rng.getrandbits(1), rng.randint(0, 40), rng.getrandbits(7)) for _ in range(k)]
        ws = [bf16(rng.getrandbits(1), rng.randint(0, 40), rng.getrandbits(7)) for _ in range(k)]
        c = (rng.getrandbits(1) << 31) | (rng.randint(0, 3) << 23) | rng.getrandbits(23)
    elif family == "floor_region":
        xs = [bf16(rng.getrandbits(1), rng.randint(40, 70), rng.getrandbits(7)) for _ in range(k)]
        ws = [bf16(rng.getrandbits(1), rng.randint(40, 70), rng.getrandbits(7)) for _ in range(k)]
        c = (rng.getrandbits(1) << 31) | (0 << 23) | rng.getrandbits(23)
    elif family == "near_overflow_no_sat":
        xs = [bf16(rng.getrandbits(1), rng.randint(180, 190), rng.getrandbits(7)) for _ in range(k)]
        ws = [bf16(rng.getrandbits(1), rng.randint(180, 190), rng.getrandbits(7)) for _ in range(k)]
        c = (rng.getrandbits(1) << 31) | (rng.randint(240, 254) << 23) | rng.getrandbits(23)
    elif family == "big_acc_small_products":
        xs = [bf16(rng.getrandbits(1), rng.randint(100, 127), rng.getrandbits(7)) for _ in range(k)]
        ws = [bf16(rng.getrandbits(1), rng.randint(100, 127), rng.getrandbits(7)) for _ in range(k)]
        c = (rng.getrandbits(1) << 31) | (rng.randint(150, 200) << 23) | rng.getrandbits(23)
    elif family == "zeros_mixed":
        xs = [0 if rng.random() < 0.5 else bf16(rng.getrandbits(1), rng.randint(0, 254), rng.getrandbits(7)) for _ in range(k)]
        ws = [0x8000 if rng.random() < 0.3 else bf16(rng.getrandbits(1), rng.randint(0, 254), rng.getrandbits(7)) for _ in range(k)]
        c = 0
    else:
        raise ValueError(family)
    return xs, ws, c


def run_targeted(pipeline, C, per=500, seed=11):
    rng = random.Random(seed)
    fams = ["realistic", "exact_cancel", "tiny_subnormal_results", "floor_region", "near_overflow_no_sat",
            "big_acc_small_products", "zeros_mixed"]
    report = {}
    for fam in fams:
        cases, refs = [], []
        while len(cases) < per:
            xs, ws, c = targeted(rng, fam)
            try:
                r = pipeline.step(c, xs, ws)
            except Exception:
                continue
            cases.append((xs, ws, c))
            refs.append(r)
        outs, fail = C.evaluate(slice_inputs(cases, 16, 16), len(cases))
        got = unslice(outs["c_out"], len(cases))
        mism = sum(1 for a, b in zip(got, refs) if a != b)
        classes = {}
        for r in refs:
            classes[classify(r)] = classes.get(classify(r), 0) + 1
        report[fam] = {"cases": per, "mismatches": mism, "assert_fail": bin(fail).count("1"), "result_classes": classes}
    return report


def real_chains(pipeline, C):
    seeds = sorted(glob.glob("/workspace/fixtures/bench-instances/v1/seeds/*/"))
    xs_all, ws_all, want = [], [], []
    for d in seeds:
        x = list(struct.unpack("<1536H", open(os.path.join(d, "x.u16"), "rb").read()))
        w = list(struct.unpack("<1536H", open(os.path.join(d, "w_row.u16"), "rb").read()))
        fx = json.load(open(os.path.join(d, "fixture.json")))
        xs_all.append(x)
        ws_all.append(w)
        want.append(fx["committed_word"])
    T = len(seeds)
    acc = [0] * T
    ref_acc = [0] * T
    step_mism = 0
    fails = 0
    for s in range(96):
        cases = [(xs_all[t][16 * s:16 * s + 16], ws_all[t][16 * s:16 * s + 16], acc[t]) for t in range(T)]
        outs, fail = C.evaluate(slice_inputs(cases, 16, 16), T)
        fails |= fail
        got = unslice(outs["c_out"], T)
        ref_acc = [pipeline.step(ref_acc[t], xs_all[t][16 * s:16 * s + 16], ws_all[t][16 * s:16 * s + 16]) for t in range(T)]
        step_mism += sum(1 for a, b in zip(got, ref_acc) if a != b)
        acc = got
    E = U.epilogue_only()
    outs, _ = E.evaluate({"u": [sum(((acc[t] >> b) & 1) << t for t in range(T)) for b in range(32)]}, T)
    y = unslice(outs["y16"], T)
    y_ref = [f32_to_bf16_word(a) for a in ref_acc]
    return {"vus": T, "steps": 96, "step_mismatches": step_mism, "assert_fail_mask": fails,
            "y_mismatch_vs_reference": sum(1 for a, b in zip(y, y_ref) if a != b),
            "y_mismatch_vs_captured_word": sum(1 for a, b in zip(y, want) if a != b)}


def negatives_file(pipeline, C):
    """The frozen vu-k1536-neg set: 'reject' instances must fire an assertion somewhere in the chain;
    'wrong' instances must produce the correct word (not the claimed one)."""
    idx = json.load(open("/workspace/fixtures/bench-instances/v1/vu-k1536-neg.index.json"))
    cols = idx["columns"]
    rows = idx["rows"]
    xb = open("/workspace/fixtures/bench-instances/v1/vu-k1536-neg.x.u16", "rb").read()
    wb = open("/workspace/fixtures/bench-instances/v1/vu-k1536-neg.w.u16", "rb").read()
    n = len(rows)
    X = [list(struct.unpack_from("<1536H", xb, 3072 * i)) for i in range(n)]
    Wt = [list(struct.unpack_from("<1536H", wb, 3072 * i)) for i in range(n)]
    ci = {c: i for i, c in enumerate(cols)}
    acc = [0] * n
    failmask = 0
    for s in range(96):
        cases = [(X[t][16 * s:16 * s + 16], Wt[t][16 * s:16 * s + 16], acc[t]) for t in range(n)]
        outs, fail = C.evaluate(slice_inputs(cases, 16, 16), n)
        failmask |= fail
        acc = unslice(outs["c_out"], n)
    E = U.epilogue_only()
    outs, _ = E.evaluate({"u": [sum(((acc[t] >> b) & 1) << t for t in range(n)) for b in range(32)]}, n)
    y = unslice(outs["y16"], n)
    res = {"reject": [0, 0], "wrong": [0, 0]}
    for t, r in enumerate(rows):
        verdict = r[ci["verdict"]]
        if verdict == "reject":
            res["reject"][0] += 1
            res["reject"][1] += (failmask >> t) & 1
        else:
            res["wrong"][0] += 1
            ok = not ((failmask >> t) & 1) and y[t] == r[ci["correct_y"]] and y[t] != r[ci["claimed_y"]]
            res["wrong"][1] += int(ok)
    return {"neg_reject_total_vs_rejected": res["reject"], "neg_wrong_total_vs_correct_word": res["wrong"]}


if __name__ == "__main__":
    for name, p in (("ampere_bf16", AMPERE_BF16_M16N8K16), ("hopper_bf16", HOPPER_BF16_M16N8K16)):
        C = U.unit(U.BF16, p.groups, p.width, p.zero_exponent)
        print(name, json.dumps(C.counts()))
        print(name, "targeted", json.dumps(run_targeted(p, C)))
        if name == "ampere_bf16":
            print(name, "real_chains", json.dumps(real_chains(p, C)))
            print(name, "negatives", json.dumps(negatives_file(p, C)))
