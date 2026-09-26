#!/usr/bin/env python3
"""red-team-flock-3: a pure-block GEMM unit netlist (`flock-unit-io/v1`, flock-backend's lowering) against the IR on every encoding:
c_out = AmpereBF16TcDot16_v1 (verity_vllm prims -> verity.ml.tc.total.tc_dot_total on AMPERE_BF16_M16N8K16) of (c, x[16], w[16]),
y16 = F2fpBf16_v1(c_out) (cvt.rn.bf16.f32, NaN -> 0x7FFF). My own reader and bit-sliced evaluator (netlist.py's row semantics:
input rows A = B = [i], the constant pinned to 1, assertion rows B = [const] with i in A), the same adversarial families as
tc_diff.py (NaN payloads, inf x 0, both-signed infinities, group saturation, cancellation, the 2^-132 floor, subnormals).

  gemm_total_diff.py NETLIST N SEED [procs]
"""
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402
import tc_diff as TD  # noqa: E402


class PureNet(NL.Net):
    """flock-unit-io/v1: header `FORMAT relation useful const n_in ni IN_COLS.. no OUT_COLS..`, then `useful` rows."""

    def __init__(self, text: str):
        self.text = text
        self.sha256 = hashlib.sha256(text.encode()).hexdigest()
        lines = text.split("\n")
        if lines[-1] == "":
            lines = lines[:-1]
        h = lines[0].split()
        self.relation, self.useful, self.const, self.n_in = h[1], int(h[2]), int(h[3]), int(h[4])
        ni = int(h[5]); self.in_cols = [int(x) for x in h[6:6 + ni]]
        no = int(h[6 + ni]); self.out_cols = [int(x) for x in h[7 + ni:7 + ni + no]]
        assert len(h) == 7 + ni + no and self.const == self.useful - 1
        self.A, self.B = [], []
        for i in range(self.useful):
            v = [int(x) for x in lines[1 + i].split()]
            na = v[0]; nb = v[1 + na]
            self.A.append(v[1:1 + na]); self.B.append(v[2 + na:2 + na + nb])
        assert len(lines) == 1 + self.useful, "trailing lines"
        self.in_words = 5          # IN_COLS 0..4: x (2 words), w (2 words), c (word 4, 32 bits)
        self.leaves = self.cut = None
        first = self.in_words * NL.WORD
        for i in range(first):
            assert (self.A[i] == [i] and self.B[i] == [i]) or (not self.A[i] and not self.B[i]), f"row {i}"
        self.inputs = [i for i in range(first) if self.A[i] == [i]]
        assert self.inputs == list(range(self.n_in)), "inputs are rows 0..n_in-1"
        self.assertions = []
        for i in range(first, self.useful):
            if i == self.const:
                continue
            assertion = self.B[i] == [self.const] and i in self.A[i]
            if assertion:
                self.assertions.append(i)
            for c in self.A[i] + self.B[i]:
                assert c < i or c == self.const or (assertion and c == i), f"row {i} reads {c}"
            assert not (self.A[i] == [i] and self.B[i] == [i]), f"free row {i}"

    def run(self, acc, x, w):
        L = len(acc); inp = {}
        for j in range(16):
            for t, p in enumerate(NL.pack_words(x[:, j], 16)):
                inp[16 * j + t] = p
            for t, p in enumerate(NL.pack_words(w[:, j], 16)):
                inp[256 + 16 * j + t] = p
        for t, p in enumerate(NL.pack_words(acc, 32)):
            inp[512 + t] = p
        z, sat = self.eval(inp)
        c = NL.unpack_word([z[self.out_cols[0] * 128 + t] for t in range(32)], L)
        y = NL.unpack_word([z[self.out_cols[1] * 128 + t] for t in range(16)], L) if len(self.out_cols) > 1 else None
        return c.astype(np.uint64), (y.astype(np.uint64) if y is not None else None), NL.unpack_mask(sat, L)


def job(args):
    netp, fam, L, seed = args
    from verity_vllm.program.registry import prims as P
    net = PureNet(open(netp).read())
    acc, a, b = TD.vectors(fam, L, seed)
    c, y, sat = net.run(acc, a, b)
    ir = np.array([P.AmpereBF16TcDot16.evaluate(int(acc[i]), *map(int, a[i]), *map(int, b[i])) & 0xFFFFFFFF for i in range(L)], dtype=np.uint64)
    iry = np.array([P.F2fpBf16.evaluate(int(v)) & 0xFFFF for v in ir], dtype=np.uint64)
    bad_c = np.nonzero(c != ir)[0]
    bad_y = np.nonzero(y != iry)[0] if y is not None else np.array([], dtype=int)
    e = (ir >> 23) & 0xFF; m = ir & 0x7FFFFF
    cls = {"nan": int(((e == 0xFF) & (m != 0)).sum()), "inf": int(((e == 0xFF) & (m == 0)).sum()), "zero": int((ir == 0).sum()),
           "subnormal": int(((e == 0) & (m != 0)).sum())}
    ex = [{"acc": f"{int(acc[i]):08x}", "x": [f"{int(v):04x}" for v in a[i]], "w": [f"{int(v):04x}" for v in b[i]],
           "net": f"{int(c[i]):08x}", "ir": f"{int(ir[i]):08x}"} for i in bad_c[:3]]
    return fam, L, len(bad_c), len(bad_y), int((~sat).sum()), cls, ex


def main():
    netp, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    net = PureNet(open(netp).read())
    print("NET", json.dumps({"sha256": net.sha256, "relation": net.relation, "rows": net.useful, "assertions": len(net.assertions),
                             "out_cols": net.out_cols, "n_in": net.n_in}), flush=True)
    chunk = 32768
    jobs = [(netp, fam, chunk, seed * 1000 + c) for fam in TD.FAMILIES for c in range(max(1, N // chunk // len(TD.FAMILIES)))]
    t0 = time.time(); tot = {}
    with Pool(procs) as pool:
        for fam, L, bc, by, unsat, cls, ex in pool.imap_unordered(job, jobs):
            t = tot.setdefault(fam, {"vectors": 0, "c_mismatches": 0, "y_mismatches": 0, "unsat": 0, "nan": 0, "inf": 0, "zero": 0, "subnormal": 0, "examples": []})
            t["vectors"] += L; t["c_mismatches"] += bc; t["y_mismatches"] += by; t["unsat"] += unsat
            for k, v in cls.items():
                t[k] += v
            t["examples"] += ex[:max(0, 3 - len(t["examples"]))]
    for fam, t in tot.items():
        print("GEMM", fam, json.dumps(t), flush=True)
    print("GEMM_SUMMARY", json.dumps({"netlist_sha256": net.sha256, "vectors": sum(t["vectors"] for t in tot.values()),
                                      "c_mismatches": sum(t["c_mismatches"] for t in tot.values()),
                                      "y_mismatches": sum(t["y_mismatches"] for t in tot.values()),
                                      "unsat": sum(t["unsat"] for t in tot.values()), "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
