"""Operand sets that isolate the sparse kernel's correctness from the base split's ΔA (for `basesplit_e2e_sm120.cu check`).

  pairs2: every 8-chunk has exactly two of its four aligned pairs nonzero (both codes of each kept pair nonzero), at
          random pair positions: the most the hardware's sparse rule allows.
  pairs1: every 8-chunk has exactly one nonzero pair, at a random position: the shape of the split's ΔA, which sits
          almost entirely on pair 0 (the sample positions at block offsets 0 and 8).
A.codes = DA.codes, so the dense and sparse variants compute the same product and each is checked against the exact sum.
Scales and B are the flat family's own (`basesplit_e2e_rows.py`), so the exponent bookkeeping (split.npz) carries over.
"""
import argparse
import os
import shutil

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="an ops/<family> directory from basesplit_e2e_rows.py")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    M, N, K = map(int, open(os.path.join(a.src, "dims.txt")).read().split())
    rng = np.random.default_rng(12)
    nonzero = np.array([c for c in range(16) if c & 7], dtype=np.uint8)
    for name, kept in (("pairs2", 2), ("pairs1", 1)):
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        codes = np.zeros((M, K // 8, 4, 2), dtype=np.uint8)
        for i in range(M):
            for c in range(K // 8):
                for p in rng.choice(4, kept, replace=False):
                    codes[i, c, p] = rng.choice(nonzero, 2)
        codes = codes.reshape(M, K)
        codes.tofile(os.path.join(d, "A.codes"))
        codes.tofile(os.path.join(d, "DA.codes"))
        for f in ("dims.txt", "A.scales", "B.codes", "B.scales", "split.npz"):
            shutil.copy(os.path.join(a.src, f), d)
        np.zeros((M, N), np.float32).tofile(os.path.join(d, "C.f32"))


if __name__ == "__main__":
    main()
