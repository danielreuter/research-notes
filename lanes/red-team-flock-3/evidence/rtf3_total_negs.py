#!/usr/bin/env python3
"""red-team-flock-3: special-value negatives for `verity/flock-pure-block-total` (relation bf16-ampere-total), end to end.

My probe (not flock-backend's write_probe): 16 VUs of K words whose outputs I choose (their accumulators chained under
`tc_dot_total`, y = F2fpBf16, the file written with flock-backend's own frame code so admission reads it). Each forged file
moves the output and y words of one VU together (negatives._rewrite_output: NV1 admits it) and runs twice with
negatives.session: an honest prover over the original file (Sigma differs) and a cheating prover holding the forged file
(Sigma agrees; only the proof can refuse). Every forgery must be refused; the honest control must be accepted. Each VU's
expected output is checked against the IR prims (AmpereBF16TcDot16 chain, F2fpBf16) before anything runs.

  rtf3_total_negs.py BIN OUTDIR [K]
"""
import json
import sys
import types
from pathlib import Path

import numpy as np

from verity_flock import instances as I, lowering as L, negatives as N

REL = "bf16-ampere-total"
ONE, PINF, NINF, MAXF, QNAN = 0x3F80, 0x7F80, 0xFF80, 0x7F7F, 0x7FC0


def vus(K):
    z = [0] * K
    def with_(pairs):
        x, w = list(z), list(z)
        for i, a, b in pairs:
            x[i], w[i] = a, b
        return x, w
    near = np.random.default_rng(20260926)
    fin = lambda: ([int((near.integers(2) << 15) | (near.integers(118, 137) << 7) | near.integers(128)) for _ in range(K)],
                   [int((near.integers(2) << 15) | (near.integers(118, 137) << 7) | near.integers(128)) for _ in range(K)])
    return [
        ("zero", with_([])),                                                  # +0
        ("subnormal", with_([(0, 0x0040, ONE)])),                             # 2^-127: FP32 0x00400000, y 0x0040
        ("nan_mixed_inf", with_([(0, PINF, ONE), (1, NINF, ONE)])),           # +inf and -inf in one group: NaN
        ("overflow_inf", with_([(i, MAXF, MAXF) for i in range(8)])),         # a saturated finite group: +inf
        ("nan_inf_times_zero", with_([(0, PINF, 0)])),                        # inf x 0: NaN
        ("neg_inf", with_([(0, NINF, ONE)])),                                 # -inf
        ("nan_across_blocks", with_([(3, 0x7F81, ONE)])),                     # a NaN in block 0's unit 0, carried through 3 blocks
        ("finite_a", fin()), ("finite_b", fin()),
    ] + [(f"finite_{i}", fin()) for i in range(7)]


#: (case, VU name, forged output word)
CASES = [
    ("zero_claimed_negative_zero", "zero", 0x8000),
    ("subnormal_claimed_flushed", "subnormal", 0x0000),
    ("mixed_inf_nan_claimed_pinf", "nan_mixed_inf", PINF),
    ("overflow_inf_claimed_max_finite", "overflow_inf", MAXF),
    ("inf_times_zero_nan_claimed_zero", "nan_inf_times_zero", 0x0000),
    ("neg_inf_claimed_nan", "neg_inf", 0x7FFF),
    ("carried_nan_claimed_quiet_nan_word", "nan_across_blocks", QNAN),
    ("finite_claimed_next_ulp", "finite_a", None),
]


def write(path, K, spec):
    pipe = L.PIPES[REL]
    x = np.asarray([s[1][0] for s in spec], dtype="<u2")
    w = np.asarray([s[1][1] for s in spec], dtype="<u2")
    accs = np.asarray(I._chain_rows((REL, x, w)), dtype=np.uint32)
    final = [I._epilogue(pipe, int(a[-1])) for a in accs]
    from verity.commitments.rowleaf import ROLE_W, ROLE_X, SCHEMA_BLAKE3_ROW
    import hashlib
    manifest = hashlib.sha256(f"rtf3-total-negs|{REL}|K={K}|n={len(spec)}".encode()).hexdigest()
    da, db = I._row_digests([r.tobytes() for r in x], "blake3", ROLE_X), I._row_digests([r.tobytes() for r in w], "blake3", ROLE_W)
    st = I._frame_v3("rtf3-total-negs", f"k{K}", manifest, 0, K, SCHEMA_BLAKE3_ROW, da, db, final, 16)
    ref = {"dataset": "rtf3-total-negs", "tier": f"k{K}", "range": [0, len(spec)], "manifest_sha256": manifest, "source": "synthetic"}
    header = {"format": I.FORMAT, "relation": REL, "vus": len(spec), "k": K, "word_bits": 16, "units": K // pipe.k, "row_bytes": 2 * K,
              "epilogue": True, "instances": ref, **{k: v for k, v in st.items() if k != "y"}}
    I._write_file(path, header, x.tobytes(), w.tobytes(), accs, final, st["y"])
    return x, w, final


def ir_out(x, w):
    from verity_vllm.program.registry import prims as P
    c = 0
    for s in range(len(x) // 16):
        c = P.AmpereBF16TcDot16.evaluate(c, *map(int, x[16 * s:16 * s + 16]), *map(int, w[16 * s:16 * s + 16])) & 0xFFFFFFFF
    return c, P.F2fpBf16.evaluate(c) & 0xFFFF


def rewrite_vu(src: Path, dst: Path, v: int, word: int) -> int:
    """negatives._rewrite_output aimed at VU ``v`` itself (that helper forges the first VU with a matching output)."""
    head, body = src.read_bytes().split(b"\n", 1)
    h = json.loads(head)
    off = 2 * h["vus"] * h["row_bytes"] + 4 * h["vus"] * h["units"]
    out = np.frombuffer(body[off:off + 4 * h["vus"]], dtype="<u4")
    marker = 0xFFFF_0000 | v
    tmp = dst.with_suffix(".tmp")
    body2 = body[:off] + np.concatenate([out[:v], [marker], out[v + 1:]]).astype("<u4").tobytes() + body[off + 4 * h["vus"]:]
    tmp.write_bytes(head + b"\n" + body2)
    got = N._rewrite_output(tmp, dst, lambda o: o == marker, word)
    tmp.unlink()
    return got


def main():
    binp, d = sys.argv[1], Path(sys.argv[2])
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
    d.mkdir(parents=True, exist_ok=True)
    (d / "net.txt").write_text(L.netlist(REL))
    spec = vus(K)
    honest = d / "honest.bin"
    x, w, final = write(honest, K, spec)
    names = [s[0] for s in spec]
    for v, nm in enumerate(names[:8]):
        c, y = ir_out(x[v], w[v])
        print("VU\t" + json.dumps({"vu": v, "name": nm, "ir_acc": f"{c:08x}", "ir_y": f"{y:04x}", "file_y": f"{final[v]:04x}",
                                   "match": y == final[v]}), flush=True)
        assert y == final[v], nm
    a = types.SimpleNamespace(bin=binp, relation=REL, prove_arg=[])
    ok = True
    r = N.session(a, honest, honest, d, 7900)
    ok &= r["accepted"]
    print("NEG\t" + json.dumps({"case": "honest_control", "expect": "accept", **r}), flush=True)
    for i, (case, nm, word) in enumerate(CASES):
        v = names.index(nm)
        if word is None:
            word = final[v] + 1
        vf = d / f"verifier-{case}.bin"
        got = rewrite_vu(honest, vf, v, word)
        assert got == v, (case, got, v)
        for j, (who, pf) in enumerate((("honest_prover", honest), ("cheating_prover", vf))):
            r = N.session(a, pf, vf, d, 7902 + 2 * i + j)
            ok &= not r["accepted"]
            print("NEG\t" + json.dumps({"case": case, "prover": who, "vu": got, "true_y": f"{final[v]:04x}", "forged_y": f"{word:04x}",
                                        "expect": "reject", "accepted": r["accepted"], "pass": not r["accepted"], "why": r["why"][:160]}), flush=True)
    print("RTF3_TOTAL_NEGATIVES\t" + json.dumps({"all_pass": bool(ok), "cases": len(CASES)}), flush=True)


if __name__ == "__main__":
    main()
