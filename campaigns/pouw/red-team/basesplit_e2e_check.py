"""The base-split break end to end, part 3 (CPU): the device's words against the exact sums, bit for bit.

Reads the operands (`basesplit_e2e_rows.py`) and the device's dumps (`basesplit_e2e_sm120.cu check`), and checks, on every
word of the operands' size:
  honest    each dense variant's word = the exact sum of A′·B̃ᵀ (the chain words are exact on these rows), and = the
            reference chain (`pearl_c4.chain`, recorded by the builder) on the sampled words;
  residual  the sparse word = the exact sum of ΔA·B̃ᵀ;
  split     sparse word + the fast A0 part (rank-1 + defect-block and hole corrections) + the patch = honest word;
  timed arm the sparse word with beta = 1 (C = the fast A0 part, float32) = fl32(exact ΔA part + C);
  negative  every variant's poisoned, never-launched buffer is rejected (no word equals its expected value).
Prints one JSON object; exit 0 only if every check holds and every negative control is rejected.
"""
import argparse
import json
import os
import sys

import numpy as np

HALF = np.array([0, 1, 2, 3, 4, 6, 8, 12, 0, -1, -2, -3, -4, -6, -8, -12], dtype=np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ops")
    ap.add_argument("dumps")
    a = ap.parse_args()
    M, N, K = map(int, open(os.path.join(a.ops, "dims.txt")).read().split())
    nb = K // 16
    sp = np.load(os.path.join(a.ops, "split.npz"))
    shift = int(sp["shift"])
    codes = np.fromfile(os.path.join(a.ops, "A.codes"), np.uint8).reshape(M, K)
    dcodes = np.fromfile(os.path.join(a.ops, "DA.codes"), np.uint8).reshape(M, K)
    bcodes = np.fromfile(os.path.join(a.ops, "B.codes"), np.uint8).reshape(N, K)
    C = np.fromfile(os.path.join(a.ops, "C.f32"), np.float32).reshape(M, N)

    def ints(c, s):
        return (HALF[c].reshape(c.shape[0], nb, 16) * s[:, :, None]).reshape(c.shape[0], K)

    Aint, DAint, Bint = ints(codes, sp["sAint"]), ints(dcodes, sp["sAint"]), ints(bcodes, sp["sBint"])
    bound = int(np.abs(Aint).max()) * int(np.abs(Bint).max()) * K
    assert bound < 2 ** 62, f"int64 bound {bound}"
    exact = Aint @ Bint.T
    exact_d = DAint @ Bint.T
    out = {"M": M, "N": N, "K": K, "shift": shift, "exact_bits_max": int(np.abs(exact).max()).bit_length()}

    def as_int(D):
        v = D.astype(np.float64) * 2.0 ** (-shift)
        return v, np.all(v == np.round(v))

    def load(name):
        p = os.path.join(a.dumps, name)
        return np.fromfile(p, np.float32).reshape(M, N) if os.path.exists(p) else None

    ok = True
    honest = None
    for var in ("dense128", "dense256"):
        D = load(f"{var}.D.f32")
        if D is None:
            continue
        v, integral = as_int(D)
        eq = v == exact.astype(np.float64)
        chain = [int(D.view(np.uint32)[i, j]) == int(c) for i, j, c in sp["chain_words"]]
        out[var] = {"words_equal_exact": int(eq.sum()), "words": M * N, "integral": bool(integral),
                    "chain_sample_equal": f"{sum(chain)}/{len(chain)}"}
        ok &= bool(eq.all()) and all(chain)
        honest = v if honest is None else honest
        neg = load(f"{var}.negctl.f32")
        out[var]["negative_control"] = "REJECT" if not np.any(neg == D) and np.all(neg.view(np.uint32) == 0xA5A5A5A5) \
            else "ACCEPTED (bad)"
        ok &= out[var]["negative_control"] == "REJECT"
    Ds = load("sparse.D.f32")
    if Ds is not None:
        v, integral = as_int(Ds)
        eq = v == exact_d.astype(np.float64)
        split = (v + sp["A0fast"].astype(np.float64) + sp["patch_words"].astype(np.float64)) == honest
        out["sparse"] = {"words_equal_exact_residual": int(eq.sum()), "integral": bool(integral),
                         "split_words_equal_honest": int(split.sum()), "words": M * N,
                         "A0_share_of_word_mean": float(np.mean(np.abs(sp["A0fast"]) / np.maximum(np.abs(exact), 1)))}
        ok &= bool(eq.all()) and bool(split.all())
        DC = load("sparse.DC.f32")
        want = (exact_d.astype(np.float64) * 2.0 ** shift + C.astype(np.float64)).astype(np.float32)
        out["sparse"]["beta1_words_equal_fl32"] = int((DC == want).sum())
        ok &= bool((DC == want).all())
        neg = load("sparse.negctl.f32")
        out["sparse"]["negative_control"] = "REJECT" if not np.any(neg == Ds) else "ACCEPTED (bad)"
        ok &= out["sparse"]["negative_control"] == "REJECT"
    out["verdict"] = "ACCEPT" if ok else "FAIL"
    print(json.dumps(out, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
