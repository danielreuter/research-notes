"""agkr-bound: gap_alt_operand against the bit link's checks, prime side only (scaffold: the link protocol is NOT built,
no cell counts).  The same honest witness and altered operand (VU v, word t: x ^= 1 with w = +-0, public words honest) as
20_link_unit.py, whose in-unit proof ACCEPTS the altered witness with its own bits (alt_alt_bits).  Here:

  digest      the altered x row's leaf digest vs the committed one: the binary side (Flock SHA-256 over the committed
              digest) can only open the HONEST preimage, so its link value z is the honest bits' value
  dense       z = sum_i eq(r, i) b_i in GF(2^128) over the unit bits in prime-side order (the honest binary side's bits
              mapped by the operand-to-message layout, taken as given here), m = ceil(log2 N) public coins r;
              per bit plane t the prime side needs S_t = sum_i bit_t(eq_i) b_i = 2 u_t + z_t with 0 <= u_t < 2^29
  combine     sum_t rho_t (S_t - 2 u_t - z_t) in BabyBear^6 with u_t = floor(S_t / 2): 0 for the honest bits, nonzero
              for the altered ones (a parity-mismatched plane has an odd residual no range-valid u_t fixes)

    [REL=bf16-ampere LEAF=sha256] python 25_gap_dense.py STMT OUT [N] [THREADS]      (cwd backends/gkr)
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import triton
import triton.language as tl

sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import bench_result as br                              # noqa: E402
from gpu import commit as CM                           # noqa: E402
from gpu.circuit import parse_circuit                  # noqa: E402

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
NT = int(sys.argv[4]) if len(sys.argv) > 4 else 13
REL, LEAF = os.environ.get("REL", "bf16-ampere"), os.environ.get("LEAF", "sha256")
FP8 = REL.startswith("fp8")
BITS = 8 if FP8 else 16
P = 2**31 - 2**27 + 1
MASK = (1 << 128) - 1
dev = torch.device("cuda")
OUT.mkdir(parents=True, exist_ok=True)
names = parse_circuit((S / "circuit.txt").read_text()).col_names
k = (names.index("y.s") - 5) // 2
COLS = list(range(5, 5 + 2 * k))
src = Path(br.__file__).resolve().parents[2]
frozen = src / "fixtures" / "bench-instances" / "v1" / "manifest.json"

from gpu.v2.fp8 import relation_params                 # noqa: E402
from gpu.v2.witness import Generator, Ops              # noqa: E402
from verity.commitments.rowleaf import ROLE_X          # noqa: E402

if REL == "bf16-ampere":
    from verity_numerical.checker import REAL          # noqa: E402

    x, W, y0, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), frozen, br.TIER, 0, N)
    params = REAL
else:
    x, W, y0, rel = br.load_relation(REL, src, 0, N, NT)
    params = relation_params(rel)[0]
X = np.array(x, dtype=np.uint16)
yw = 4 if y0.dtype == np.uint32 else 2
ops = Ops("cuda")
gen = Generator(ops, params)
iset = CM.instance_set(REL, 0, N, src, frozen)
C = CM.commit(LEAF, REL, iset, 0, X, W, np.asarray(y0).reshape(N, 1), yw)
ci = torch.tensor(COLS, device=dev)
sh = torch.arange(BITS, device=dev)


def rows_for(xx):
    return gen.run(ops.asarray(xx), ops.asarray(W), ops.asarray(y0))


def bits_of(units: torch.Tensor) -> torch.Tensor:
    v = units.index_select(1, ci)
    return ((v[:, :, None] >> sh) & 1).reshape(-1).to(torch.uint8)


honest_rows = rows_for(X)
assert int(honest_rows.bad.sum()) == 0
hb = bits_of(honest_rows.units)
alt = None
zero = (0x00, 0x80) if FP8 else (0x0000, 0x8000)
cands = ((v, int(t)) for v in range(N) for t in np.nonzero(np.isin(W[v], zero))[0] if not (FP8 and (int(X[v, t]) & 0x7F) >= 0x7E))
for tried, (v, t) in enumerate(cands):
    if tried >= 12:
        break
    xx = X.copy()
    xx[v, t] ^= 1
    rows = rows_for(xx)
    if int(rows.bad.sum()) == 0:
        alt = (v, t, xx, rows)
        break
if alt is None:
    raise SystemExit("no altered operand keeps the public words honest")
v, t, xalt, alt_rows = alt
ab = bits_of(alt_rows.units)
del honest_rows, alt_rows
NB = hb.numel()
diff = torch.nonzero(hb != ab).reshape(-1)
print(f"{REL}+{LEAF}: altered VU {v} word {t} x {int(X[v, t]):#x} -> {int(xalt[v, t]):#x} (w {int(W[v, t]):#x}); "
      f"{NB} link bits, {diff.numel()} differ (units {sorted({int(i) // (2 * k * BITS) for i in diff.tolist()})[:8]}...)", flush=True)

d_alt = CM.row_digests(xalt[v:v + 1], iset.word_bits, ROLE_X, LEAF)[0]
d_hon = CM.row_digests(X[v:v + 1], iset.word_bits, ROLE_X, LEAF)[0]
digest = {"committed": C.digests["a"][v].hex(), "honest_recomputed": d_hon.hex(), "altered": d_alt.hex(),
          "honest_matches_commitment": d_hon == C.digests["a"][v], "altered_matches_commitment": d_alt == C.digests["a"][v]}
print(f"digest: committed {digest['committed'][:16]}.. honest {digest['honest_recomputed'][:16]}.. altered {digest['altered'][:16]}.. "
      f"(altered matches: {digest['altered_matches_commitment']})", flush=True)

M = math.ceil(math.log2(NB))
rng = np.random.default_rng(int.from_bytes(os.urandom(8), "little"))


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


def split(val: int):
    s = lambda z: z - (1 << 64) if z >> 63 else z
    return s(val & ((1 << 64) - 1)), s(val >> 64)


r = [int.from_bytes(rng.bytes(16), "little") for _ in range(M)]
tabs = np.zeros((M, 16, 256, 2), dtype=np.int64)
for j in range(M):
    for kk in range(16):
        base = [gmul(1 << (8 * kk + q), r[j]) for q in range(8)]
        for b in range(256):
            acc = 0
            for q in range(8):
                if (b >> q) & 1:
                    acc ^= base[q]
            tabs[j, kk, b] = split(acc)
tabs = torch.from_numpy(tabs).to(dev)


@triton.jit
def eq_level(T, TB, TAB, h, BLOCK: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < h
    lo = tl.zeros([BLOCK], dtype=tl.int64)
    hi = tl.zeros([BLOCK], dtype=tl.int64)
    for kk in tl.static_range(16):
        b = tl.load(TB + i * 16 + kk, mask=m, other=0).to(tl.int64)
        lo ^= tl.load(TAB + (kk * 256 + b) * 2, mask=m, other=0)
        hi ^= tl.load(TAB + (kk * 256 + b) * 2 + 1, mask=m, other=0)
    tl.store(T + (i + h) * 2, lo, mask=m)
    tl.store(T + (i + h) * 2 + 1, hi, mask=m)
    tl.store(T + i * 2, tl.load(T + i * 2, mask=m, other=0) ^ lo, mask=m)
    tl.store(T + i * 2 + 1, tl.load(T + i * 2 + 1, mask=m, other=0) ^ hi, mask=m)


T = torch.zeros((1 << M, 2), dtype=torch.int64, device=dev)
T[0, 0] = 1
tb = T.view(torch.uint8).view(1 << M, 16)
for j in range(M):
    h = 1 << j
    eq_level[(triton.cdiv(h, 1024),)](T, tb, tabs[j], h, BLOCK=1024)
for i in (0, int(diff[0]), NB - 1):
    want = 1
    for j in range(M):
        want = gmul(want, r[j] if (i >> j) & 1 else r[j] ^ 1)
    assert (int(T[i, 0]) & ((1 << 64) - 1)) | ((int(T[i, 1]) & ((1 << 64) - 1)) << 64) == want, f"eq({i}) mismatch"
sh8 = torch.arange(8, device=dev, dtype=torch.int32)


def planes(bv: torch.Tensor) -> torch.Tensor:
    out = torch.zeros(128, dtype=torch.int64, device=dev)
    for s in range(0, NB, 1 << 20):
        sel = tb[s:s + (1 << 20)][bv[s:s + (1 << 20)].bool()].to(torch.int32)
        out += ((sel[:, :, None] >> sh8) & 1).reshape(-1, 128).sum(0, dtype=torch.int64)
    return out


def gf(bits_t: torch.Tensor) -> int:
    return sum(int(b) << q for q, b in enumerate(bits_t.tolist()))


t0 = time.perf_counter()
S_h, S_a = planes(hb), planes(ab)
torch.cuda.synchronize(dev)
tp = time.perf_counter() - t0
z = S_h & 1
zdiff = 0
for i in diff.tolist():
    zdiff ^= (int(T[i, 0]) & ((1 << 64) - 1)) | ((int(T[i, 1]) & ((1 << 64) - 1)) << 64)
assert gf(z) ^ gf(S_a & 1) == zdiff, "plane parities disagree with the XOR of eq over the differing bits"
rho = torch.from_numpy(rng.integers(0, P, size=(128, 6), dtype=np.int64)).to(dev)


def combine(S_):
    u = S_ >> 1
    assert int(u.max()) < (1 << 29)
    d = S_ - 2 * u - z
    return d, [int(c) for c in ((rho * (d % P)[:, None]).sum(0) % P).tolist()]


d_h, c_h = combine(S_h)
d_a, c_a = combine(S_a)
res = {"relation": C.relation, "vus": N, "link_bits": NB, "m": M, "altered": {"vu": v, "word": t, "x_frozen": int(X[v, t]),
       "x_altered": int(xalt[v, t]), "w": int(W[v, t])}, "differing_bits": diff.numel(), "digest": digest,
       "z_honest_hex": f"{gf(z):032x}", "z_prime_altered_hex": f"{gf(S_a & 1):032x}",
       "planes_mismatched_altered": int((d_a != 0).sum()), "planes_mismatched_honest": int((d_h != 0).sum()),
       "combination_honest": c_h, "combination_altered": c_a, "planes_s_both": tp}
res["ok"] = (digest["honest_matches_commitment"] and not digest["altered_matches_commitment"] and res["planes_mismatched_honest"] == 0
             and res["planes_mismatched_altered"] > 0 and not any(c_h) and any(c_a))
print(f"z honest {res['z_honest_hex']} vs prime-side altered {res['z_prime_altered_hex']}; parity-mismatched planes: honest "
      f"{res['planes_mismatched_honest']}, altered {res['planes_mismatched_altered']} / 128; BabyBear^6 combination honest {c_h} altered {c_a}",
      flush=True)
(OUT / "gap_dense.json").write_text(json.dumps(res, indent=1, default=str))
print("GAP-DENSE OK" if res["ok"] else "GAP-DENSE FAILED", flush=True)
sys.exit(0 if res["ok"] else 1)
