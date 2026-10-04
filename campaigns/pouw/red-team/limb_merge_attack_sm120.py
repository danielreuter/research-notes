"""`fp8-limb-rate/sm120` and `fp8-merge-rate/sm120`: a targeted in-domain family at the domain's edge.

Every in-domain element carries noise of about ρ·α (σ = ρ, δ = 1) with ρ·α ≥ 1, so an E4M3 code is deterministic only
far above ρ. A 16-block always holds two of ρ's every-8th sample positions, so a block of deterministic codes puts
spikes into ρ itself. This family spends that budget as well as it can:
- one row-max entry of size L (off the sample positions) sets α, and so the noise floor ρ·α;
- n_b aligned blocks of `run` entries (the same columns in every row; a run of 16 for NVFP4 blocks, 32 for merge
  fragments; `run` = 64 puts four blocks in one NVFP4 k64 atom) are all at V, chosen so that α·V lands on `target`,
  an E4M3 value that is also an NVFP4 value (256 = 4·64, 128 = 2·64: 128 ± 128 are E4M3, 256 + 256 overflows);
- the rest is N(0, 1).
Each config is formed exactly (`pearl_c.form_v1` on the sm_120 device, seeds as the scheme draws them) and kept only
when every row is in the domain (ρ·α ≥ 1 and `live_row`). Reported per config:
- blk: the share of (row, 16-block) all of whose codes are one NVFP4 block (a UE4M3 scale s with every code in ±s·E2M1);
- atomA: the share of NVFP4 A-fragments (16 rows x k64) all of whose 64 blocks are;
- merge: the share of 16 x 32 fragments whose quadrant pairs (i, l) + (i + T/2, l + k/2) all sum and subtract to E4M3.
Usage: PYTHONPATH=<tree>/packages/verity/src:<tree>/protocols/pouw python3 limb_merge_attack_sm120.py [k] [T] [procs]
"""
import itertools
import json
import multiprocessing as mp
import random
import struct
import sys

from verity_pouw.schemes import pearl_c as C
from verity_pouw.schemes import pearl_c_device as D
from verity_pouw.schemes import pearl_kw as P

E2M1 = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)
VALS = []
for c in range(256):
    try:
        VALS.append(P.fp8_to_f32(c))
    except P.Reject:
        VALS.append(None)
E4M3 = {v for v in VALS if v is not None}
SCALES = sorted({abs(v) for v in VALS if v is not None and v > 0})


def f32(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def nvfp4_block(vals):
    mags = [abs(v) for v in vals]
    for s in SCALES:
        if all(m / s in E2M1 for m in mags):
            return True
    return False


def merges(a, b):
    return a is not None and b is not None and (a + b) in E4M3 and (a - b) in E4M3


def run_config(cfg):
    k, T, L, target, n_b, run, seed = cfg
    rng = random.Random(f"limb-merge/{k}/{T}/{L}/{target}/{n_b}/{run}/{seed}")
    starts = [b * run for b in range(0, k // run, max(1, (k // run) // max(n_b, 1)))][:n_b]
    starts += [s + k // 2 for s in starts if s + k // 2 + run <= k and s < k // 2]
    spiky = {l for s in starts for l in range(s, s + run)}
    max_pos = next(l for l in range(1, k) if l % 8 and l not in spiky)
    rows = []
    for _ in range(T):
        x = [rng.gauss(0, 1) for _ in range(k)]
        x[max_pos] = float(L)
        rows.append(x)
    # V such that α·V = target, with α from the row's own stats once the spikes are in: fixed point on V.
    V = 1.0
    for _ in range(40):
        for x in rows:
            for l in spiky:
                x[l] = V
        words = [[f32(v) for v in x] for x in rows]
        alphas = [P.f32_of_bits(C.s5_stats(w)[2]) for w in words]
        V_new = target / (sum(alphas) / len(alphas))
        if abs(V_new - V) < 1e-9 * V_new:
            break
        V = V_new
    words = [[f32(v) for v in x] for x in rows]
    for w in words:
        s, rho, alpha, _ = C.s5_stats(w)
        if P.f32_of_bits(rho) * P.f32_of_bits(alpha) < 1.0 or not C.live_row(w):
            return dict(k=k, T=T, L=L, target=target, n_b=n_b, run=run, seed=seed, V=V, in_domain=False)
    salt = f"limb-merge/{k}/{L}/{target}/{n_b}/{run}/{seed}".encode()
    seed_b = C._labelled(salt + b"B", "seed-B")
    seed_a = C._labelled(salt + b"A", "seed-A")
    e = [P.sample_line(seed_a, 0, 0, i) for i in range(T)]
    F = C._basis(seed_b, 0, k, C.LINE_NORM_V1)
    formed = C.form_v1(words, e, F, D.SM120)
    A = [[VALS[c] for c in row] for row in formed.codes]
    rho_alpha = [P.f32_of_bits(r) * P.f32_of_bits(a) for r, a in zip(formed.rho, formed.alpha)]
    blk_ok = [[nvfp4_block(row[b:b + 16]) for b in range(0, k, 16)] for row in A]
    blk = sum(map(sum, blk_ok)) / (T * (k // 16))
    spiky_blocks = sorted({l // 16 for l in spiky})
    blk_spiky = (sum(blk_ok[i][b] for i in range(T) for b in spiky_blocks) / (T * len(spiky_blocks))
                 if spiky_blocks else 0.0)
    atoms = [all(blk_ok[i][b] for i in range(fi, fi + 16) for b in range(a4, a4 + 4))
             for fi in range(0, T - 15, 16) for a4 in range(0, k // 16, 4)]
    h, kh = T // 2, k // 2
    ok = [[merges(A[i][l], A[i + h][l + kh]) for l in range(kh)] for i in range(h)]
    frags = [all(ok[i][l] for i in range(fi, fi + min(16, h)) for l in range(fl, fl + 32))
             for fi in range(0, h, 16) for fl in range(0, kh, 32)]
    spike_codes = sorted({A[i][l] for i in range(T) for l in spiky})[:6]
    return dict(k=k, T=T, L=L, target=target, n_b=n_b, run=run, seed=seed, V=V, in_domain=True,
                rho_alpha_min=min(rho_alpha), blk=blk, blk_spiky=blk_spiky, atomA=sum(atoms) / max(1, len(atoms)),
                atoms=len(atoms), merge=sum(frags) / max(1, len(frags)), frags=len(frags), spike_codes=spike_codes)


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
    T = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else mp.cpu_count()
    grid = []
    for L, target, n_b, run in itertools.product((60, 120, 240, 440), (256.0, 128.0), (1, 2, 4, 8, 16), (16, 32, 64)):
        grid.append((k, T, L, target, n_b, run, 0))
    with mp.Pool(procs) as pool:
        for r in pool.imap_unordered(run_config, grid):
            print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
