"""agkr-bound: the survey §3.8 link's dense check on the A100, prover side, for N committed bits (default one 4,096-VU
BF16 batch: 393,216 units x 512 = 201,326,592), with random public-coin values (a cost model, not the protocol):

  eq       eq(r, i) over GF(2^128) for all i < 2^m (m = ceil log2 N), by doubling; each level multiplies by the constant
           r_j with 16 byte tables (x^128 + x^7 + x^2 + x + 1), T(1 + r_j) = T ^ T r_j
  coef     c_i = sum_t rho_t bit_t(eq(r, i)) in BabyBear^6 (the 128 integer identities batched by rho), 16 byte tables
  ip       sum_i c_i b_i over the committed bits b (the functional's prover-side combination)

then the u_t second-round commitment (128 values of ceil log2 N + 1 bits) as its own single-segment Ligero proof
(tools/link_stub.py circuit: booleanity + recomposition).  cwd backends/gkr.
    python 21_dense_gpu.py [N] [REPS]
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, ".")
sys.path.insert(0, "tools")

P = 2**31 - 2**27 + 1
N = int(sys.argv[1]) if len(sys.argv) > 1 else 393216 * 512
REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
dev = torch.device("cuda")
rng = np.random.default_rng(20260925)
M = math.ceil(math.log2(N))
MASK = (1 << 128) - 1


def gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a = (a & MASK) ^ 0x87
    return r


def split(v: int) -> tuple[int, int]:
    lo, hi = v & ((1 << 64) - 1), v >> 64
    s = lambda x: x - (1 << 64) if x >> 63 else x
    return s(lo), s(hi)


def const_tables(c: int) -> torch.Tensor:
    t = np.zeros((16, 256, 2), dtype=np.int64)
    for k in range(16):
        for b in range(256):
            t[k, b] = split(gmul(b << (8 * k), c))
    return torch.from_numpy(t).to(dev)


def bytes_of(x: torch.Tensor) -> list[torch.Tensor]:
    lo, hi = x[:, 0], x[:, 1]
    return [((lo >> (8 * k)) & 255) for k in range(8)] + [((hi >> (8 * k)) & 255) for k in range(8)]


def cmul(x: torch.Tensor, tab: torch.Tensor) -> torch.Tensor:
    acc = None
    for k, b in enumerate(bytes_of(x)):
        v = tab[k][b]
        acc = v if acc is None else acc ^ v
    return acc


r = [int.from_bytes(rng.bytes(16), "little") for _ in range(M)]
tabs = [const_tables(rj) for rj in r]
rho = rng.integers(0, P, size=(128, 6), dtype=np.int64)
U = np.zeros((16, 256, 6), dtype=np.int64)
for k in range(16):
    for b in range(256):
        U[k, b] = sum((rho[8 * k + s] for s in range(8) if (b >> s) & 1), np.zeros(6, dtype=np.int64)) % P
U = torch.from_numpy(U).to(dev)
bits = torch.from_numpy(rng.integers(0, 2, size=N, dtype=np.int8)).to(dev)
CH = 1 << 22


def eq_table() -> torch.Tensor:
    t = torch.zeros((1, 2), dtype=torch.int64, device=dev)
    t[0, 0] = 1
    for j in range(M):
        p = torch.cat([cmul(t[s:s + CH], tabs[j]) for s in range(0, t.shape[0], CH)])
        t = torch.cat([t ^ p, p])
    return t[:N]


def coef_ip(eq: torch.Tensor) -> tuple[torch.Tensor, float, float]:
    acc = torch.zeros(6, dtype=torch.int64, device=dev)
    tc = ti = 0.0
    for s in range(0, N, CH):
        torch.cuda.synchronize(dev)
        t0 = time.perf_counter()
        bs = bytes_of(eq[s:s + CH])
        c = U[0][bs[0]]
        for k in range(1, 16):
            c = c + U[k][bs[k]]
        c = c % P
        torch.cuda.synchronize(dev)
        t1 = time.perf_counter()
        acc = (acc + (c * bits[s:s + CH, None].long()).sum(0)) % P
        torch.cuda.synchronize(dev)
        tc += t1 - t0
        ti += time.perf_counter() - t1
    return acc, tc, ti


runs = []
for rep in range(REPS + 1):
    torch.cuda.synchronize(dev)
    torch.cuda.reset_peak_memory_stats(dev)
    t0 = time.perf_counter()
    eq = eq_table()
    torch.cuda.synchronize(dev)
    te = time.perf_counter() - t0
    acc, tc, ti = coef_ip(eq)
    runs.append({"rep": rep - 1, "eq_s": te, "coef_s": tc, "ip_s": ti, "total_s": te + tc + ti, "peak_mem_bytes": torch.cuda.max_memory_allocated(dev)})
    print(json.dumps(runs[-1]), flush=True)
    del eq
# spot check: eq(r, i) for a few i against the product formula
eq = eq_table()
for i in (0, 1, N // 3, N - 1):
    want = 1
    for j in range(M):
        want = gmul(want, r[j] if (i >> j) & 1 else r[j] ^ 1)
    lo, hi = int(eq[i, 0]) & ((1 << 64) - 1), int(eq[i, 1]) & ((1 << 64) - 1)
    assert lo | (hi << 64) == want, f"eq({i}) mismatch"
print(f"eq spot checks OK (m = {M})", flush=True)
del eq

import link_stub as LS                                  # noqa: E402
from gpu import prover                                  # noqa: E402
from gpu.circuit import layers, parse_circuit           # noqa: E402

ub = M + 1
b, info = LS.build(1, ub, 1)
circ = parse_circuit(b.text())
w = torch.from_numpy(LS.witness(128, 1, ub, 1, 7).astype(np.int64)).to(dev) % P
inst = prover.Instance([prover.Segment("u", circ, layers(circ), w, circ.hash)], None)
ut = []
for rep in range(REPS + 1):
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize(dev)
    tp = time.perf_counter() - t0
    try:
        prover.verify(inst, proof, True)
        py = "accept"
    except prover.VerifyError as e:
        py = f"reject ({e})"
    ut.append({"rep": rep - 1, "prove_s": tp, "python": py, "proof_bytes": proof.nbytes(), "committed_elements": st.committed_elements})
    print(json.dumps(ut[-1]), flush=True)
med = lambda xs: float(np.median(xs))
summary = {"N": N, "m": M, "eq_s": med([x["eq_s"] for x in runs[1:]]), "coef_s": med([x["coef_s"] for x in runs[1:]]),
           "ip_s": med([x["ip_s"] for x in runs[1:]]), "total_s": med([x["total_s"] for x in runs[1:]]),
           "u_t": {"values": 128, "bits": ub, "prove_s": med([x["prove_s"] for x in ut[1:]]), "proof_bytes": ut[-1]["proof_bytes"],
                   "committed_elements": ut[-1]["committed_elements"]}}
print("SUMMARY " + json.dumps(summary), flush=True)
Path("/workspace/agkr-bound/dense").mkdir(parents=True, exist_ok=True)
Path("/workspace/agkr-bound/dense/dense_gpu.json").write_text(json.dumps({"runs": runs, "u_t": ut, "summary": summary}, indent=1))
