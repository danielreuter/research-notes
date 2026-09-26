#!/usr/bin/env python3
"""red-team-flock-3: teeth of tc_diff.py. One-row mutants of the attention unit netlist (an operand of an AND row replaced by
another earlier column) must show mismatches against the IR on the same adversarial families.

  tc_mutants.py NETLIST MUTANTS SEED
"""
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402
import tc_diff as TD  # noqa: E402


def main():
    netp, k, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    from verity_vllm.program.registry import prims as P
    text = open(netp).read()
    lines = text.split("\n")
    base = NL.Net(text)
    first = base.in_words * NL.WORD
    rng = random.Random(seed)
    vecs = [TD.vectors(f, 2048, seed) for f in TD.FAMILIES]
    ir = [np.array([P.AmpereBF16TcDot16.evaluate(int(acc[i]), *map(int, a[i]), *map(int, b[i])) & 0xFFFFFFFF for i in range(len(acc))],
                   dtype=np.uint64) for acc, a, b in vecs]
    for m in range(k):
        while True:
            r = rng.randrange(first, base.useful - 1)
            if base.A[r] and base.B[r] and base.B[r] != [base.const] and r not in base.assertions:
                break
        A = list(base.A[r]); j = rng.randrange(len(A))
        A[j] = rng.choice([c for c in range(first, r) if c not in A] or [0])
        row = f"{len(A)} {' '.join(map(str, A))} {len(base.B[r])} {' '.join(map(str, base.B[r]))}"
        mut = lines[:1 + r] + [row] + lines[2 + r:]
        tc = NL.TcUnit(NL.Net("\n".join(mut)))
        bad = 0
        for (acc, a, b), want in zip(vecs, ir):
            res, sat = tc(acc, a, b)
            bad += int(((res != want) | ~sat).sum())
        print(f"MUTANT {m}: row {r} operand {j} -> {A[j]}: {bad} of {sum(len(x[0]) for x in vecs)} vectors differ from the IR", flush=True)


if __name__ == "__main__":
    main()
