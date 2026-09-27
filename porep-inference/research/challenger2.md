# RQ5: bandwidth challenger under threat model v2 -- kernel, jitter under decode load, tiers, protocol

Agent P1 (protocol + measurement), 2026-09-03, pod c (H100 SXM 80 GB HBM3, 132 SMs, CUDA 12.4, torch 2.4.1),
GPU shared with W1 under `/workspace/gpu.lock` until W1 finished (the 20:30 final runs had the GPU alone). Code: `porep/challenge/` (extension `challenge_kernels.cu`,
Python `Challenger` / NumPy `Verifier`), `porep/bench/challenge_bench.py` (test / bw / lat / tier),
`porep/bench/challenge_load.py` (background decode load), `porep/bench/challenge_runs.sh` (campaign stages).
Data: `results/phase2/rq5/*.csv` on the pod (pulled to `results/pod-c/phase2/rq5/`), each with a `.cmd` sidecar.
Protocol spec: `research/protocol2.md`. Log entries are dated (PT); the summary on top was written last.

## Summary / recommendations

**Kernel.** A Shacham-Waters position-wise linear MAC over `F_(2^61-1)` (`sw`: one `IMAD.WIDE` + a 128-bit
accumulate per 4-byte word, one Mersenne reduction per position at the end, 64 KB response) reads random
32 KB sectors of a 70 GB region at **3.09-3.12 TB/s = 97-98 % of the sequential-read ceiling (3.18 TB/s),
93 % of the 3.35 TB/s spec, and above the D2D memcpy traffic rate (3.02-3.04 TB/s)**; 8-16 KB sectors are
within 2-4 %, 4 KB sectors lose 15 % (2.6-2.7 TB/s). The MAC is free relative to the raw random read. It is
bit-exact against a NumPy reference; the verifier check needs one 8-byte tag per sector (20 MB for 80 GB)
and 3.6 ms of one CPU core per 4 GB challenge in NumPy (131 k PRF + 139 k mulmod; ~0.5 ms in C). A
per-sector keyed fingerprint (`fp`, for the Merkle-only variant) runs at 1.9 TB/s in its current form.

**Honest response time** (isolated Poisson launches, idle GPU): `T` = 0.547 / 1.314 / 2.590 ms for X =
1.6 / 4 / 8 GB at 32 KB sectors, p99.9 - p50 = 0.09-0.13 ms.

**Under decode load, X = 4 GB** (kernel event time, p50 / p99 / p99.9, ms; idle 1.314 / 1.377 / 1.445):

| how the challenger is scheduled | load | p50 | p99 | p99.9 | p99.9 - idle p50 |
|---|---|---|---|---|---|
| separate process (time-slicing, no MPS), doorbell-to-response | Qwen-7B decode, plaintext, B=16 | 2.62 | 3.70 | 3.77 | **2.45** (waits for the load's ~2.5 ms time slice) |
| same process, own stream (priority irrelevant) | Qwen-7B decode, plaintext | 1.357 | 1.619 | 1.681 | **0.37** |
| same process, own stream | Qwen-7B decode, phase-1 **encoded** weights (persistent-CTA decode kernels) | 1.483 | 2.680 | 3.284 | **1.97** (max 5.7 ms at 1.6 GB) |
| same process, own stream | Qwen-7B decode, encoded weights, decode kernel re-launched with **one CTA per block** | 1.400 | 1.476 | 1.684 | **0.37** |
| same process, own stream | synthetic: persistent-CTA decode + GEMMs | 2.066 | 3.254 | 3.299 | 1.98 |
| same process, own stream | synthetic: **one-block-CTA** decode + GEMMs | 1.409 | 1.451 | 1.493 | **0.18** |
| **final, merged phase-2 kernels, security point (4,6,3) drU mixer 1, 5/s** (20:30 entry; idle p50 1.324) | unfused ping-pong `POREP_BPC=2` (K1 default) | 1.404 | 1.474 | 1.662 | **0.34** pass |
| " | unfused `POREP_BPC=0` (persistent) | 1.491 | 2.781 | 3.147 | 1.82 fail |
| " | `fusedmm` persistent (K2 default) | 1.499 | 3.390 | 3.724 | 2.40 fail |
| " | **`fusedmm` `POREP_FUSED_BPC=auto4`** | 1.375 | 1.437 | 1.494 | **0.17** pass, recommended |
| " | `fusedmm` `POREP_FUSED_BPC=auto2` | 1.353 | 1.415 | 1.435 | **0.11** pass |
| " | plaintext Qwen step (reference) | 1.362 | 1.613 | 1.703 | 0.38 |

The jitter is not HBM contention (once running, the challenger owns the SMs and reads at the idle rate; the
load is stalled for exactly `T`, 0.66 % of throughput at 5/s); it is the wait for the load's *resident CTAs
to drain*. Consequences: (1) the challenge kernel must run **inside the serving process** (a separate
context adds a uniform 0-2.5 ms scheduler wait); (2) it must **take the SMs exclusively** (1024-thread CTAs;
co-resident 128-thread CTAs get half the bandwidth); (3) **every kernel in the serving process needs bounded
CTA lifetime** (<= ~50 us) or a yield flag -- the phase-1 decode / fused-GEMV kernels are persistent-grid
(`min(nblocks, 528)` CTAs living 0.3-3 ms) and push p99.9 to 2 ms; re-launching the same decode kernel
with `grid = nblocks` (one 64 KB block per CTA; a one-line change, tested via a monkeypatch in
`challenge_load.py`) brings the encoded-weights Qwen load to 0.37-0.41 ms -- the same tail as the plaintext
model, now set by the remaining cuBLAS / attention kernels -- and makes the load 2 % *faster*. **Pass
criterion (p99.9 jitter <= ~0.3 ms at <= 1 % HBM time): 0.18 ms when every kernel has bounded CTAs,
0.37-0.41 ms with the stock library kernels (marginal, 1.2-1.4x over), 1.8-2.0 ms (6x) with the phase-1
decode kernels as they are.** Recommended slack: 0.5 ms.

**Final verification with the merged phase-2 kernels (20:30 entry, `jitter_final.csv`)**: K1 and K2 adopted
the bounded-CTA requirement and it works on the real security-point load ((4,6,3) drU mixer 1, Qwen-7B
B = 16, 2000 challenges at 5/s): p99.9 - idle p50 = **0.34 ms unfused (`POREP_BPC=2`, K1 default), 0.17 ms
`fusedmm` `POREP_FUSED_BPC=auto4`, 0.11 ms `auto2`** vs 1.82 / 2.40 ms for the persistent variants
(`POREP_BPC=0`, K2's `fusedmm` default). The pass criterion holds in every bounded mode and the bounded fused
modes beat the plaintext model's own tail (0.38 ms). Cost of bounding: 0 % unfused, +1.0-1.2 % fused step
time here (K2 isolated: +3.4 % `auto4`, +8.5 % `auto2`). **Shipping default: `fusedmm` + `POREP_FUSED_BPC=auto4`**
(fastest step, 35.5 ms; 0.17 ms tail; fits a 0.3 ms slack); K2's persistent default must not ship.

**Tiers** (measured on pod c): pinned host DRAM -> GPU over PCIe Gen5 x16 = **55.5 GB/s** (copy engine),
**51.3 GB/s for a kernel reading mapped host memory, identical for sequential and random 4-64 KB sectors**
(the MAC kernel itself runs at 51 GB/s straight from host memory). NIC and NVMe share the GPU's x16 link, so
all PCIe-attached tiers together are 1.7-1.8 % of `B_HBM,eff` = 3.04 TB/s. NVLink peer (450 GB/s
published) is 15 % -- neutralised only by challenging every GPU of the NVLink domain simultaneously.

**Enforceable residual** `eps_max = B_tier / B_HBM (1 + slack / T)` with slack 0.5 ms: **2.5 % at X = 4 GB
(2.2 % at 8 GB, 3.5 % at 1.6 GB) on an 8x H100 node**; 5.3 % if the challenger has to live in a separate
context (slack 2.5 ms). GB200: C2C 8.5 % (X = 5 %), 7.2 % (X = 10 %); Grace-LPDDR-limited 4.8 / 4.1 %. A
steady cheater above `eps_max` misses every deadline: detection within 1 s at 5 challenges/s (0.66 % of HBM
time at 4 GB); intermittent cheating a fraction `f` of the time is caught with `1 - exp(-5 f N)`.

**Dedication** (measured with the phase-1 encoder, 1-block buffers): the sequential labeling chain of a
64 KB block takes **3.61 ms** at (l=3, n=2048) (0.59 us per node; 7.2 ms for 128 KB blocks), so an adversary
holding only `D` (e.g. zeros) and the seed cannot regenerate a challenged sector inside the 1.81 ms deadline
at X = 4 GB (2.0x margin; X = 8 GB needs 128 KB blocks for 2.3x). Rule: `l n t_hash >= 2 (T + slack)`.
**At the phase-2 security point the rule fails (20:30 entry, `regen_final.csv`): mixer 1 is 392 ns per node
and the block is 32 KB, so the chain is 1.61 ms < 1.81 ms deadline (0.89x). 64 KB blocks (`n = 2048`) give
3.16 ms = 1.75x (+6 % e2e on K2's path); X = 1.6 GB keeps 32 KB blocks at 1.53x with `eps_max` 3.5 %. The
spec now requires block >= 64 KB at X = 4 GB; the parameter owners must pick one of the two.**

**128-bit key**: K1's `replica_seed` (32 b) + `replica_key` (96 b) = the four key words of the hash state;
the spec's `seed = PRF_K_seed(replica id, comm_D)` fills both (all 128 bits secret, slot separation inside
the PRF input) -- spec text adjusted in protocol2.md Section 2; no protocol change.

**Recommendations.** X = 4-8 GB at 3.8-5/s, 32 KB sectors, deadline = idle `T` + 0.5 ms, all GPUs of the
node/NVLink domain at once; the challenge kernel as an agent kernel in the serving process; the RQ1/RQ2
kernels with bounded CTAs -- now the default in K1's kernel (`POREP_BPC=2`) and available in K2's
(`POREP_FUSED_BPC=auto4`, make it the default) -- the one change without which the deadline cannot be
tight; **64 KB blocks at the security point** (or X <= 1.6 GB) so the regeneration chain stays >= 1.75x the
deadline; protocol as in `protocol2.md` (Design A tags computed by the on-node challenger from a one-time
stream of `R`, 128-bit seed never leaves V; consistency openings at 1/s leaking 32 B of `D` each).

---

## 2026-09-03 08:00 -- Design decisions before touching the GPU

**What the challenger has to prove.** Under threat model v2 the only copy in HBM is the encoded replica
`R = Enc_seed(D)` (weights + sealed KV pages), pseudo-random to anyone without the seed. Point challenges
are useless for locality (2-20 us from any tier), so the challenger reads a random `X = 2-10 %` of HBM per
challenge with deadline `X / B_HBM + slack` and needs an aggregate that (i) binds every byte read, (ii) costs
the GPU far less than the read itself (H100: ~5 INT lane-ops per HBM byte at 3.35 TB/s), and (iii) the
verifier can check without holding the data.

**Aggregate = Shacham-Waters position-wise linear MAC over F_p, p = 2^61 - 1** (private verification).
Sector `j` = `s` 32-bit words `m_{j,i}`. Challenge `(nonce)` -> positions `t = 0..n-1` with sector index
`j_t = H(nonce, t) mod N` and coefficient `nu_t = H'(nonce, t)` (32-bit, odd). Response:

~~~text
mu[i] = sum_t nu_t * m_{j_t, i}   (mod p)   for every word position i in 0..s-1     (s*8 bytes: 64 KB at 32 KB sectors)
~~~

GPU cost per 4-byte word: one `IMAD.WIDE` (32x32 -> 64) plus a 128-bit accumulate (carry via compare); no
modular arithmetic inside the loop, one Mersenne reduction per position at the end: ~1.5 INT ops/byte, i.e.
~30 % of the INT issue budget at full HBM rate -- memory-bound by construction. The verifier holds one
8-byte tag per sector, `sigma_j = PRF_k(j) + <alpha, m_j> mod p` (alpha: s secret field elements, k: PRF key),
and checks `sum_t nu_t sigma_{j_t} == sum_t nu_t PRF_k(j_t) + <alpha, mu>`. Soundness: a prover missing
sector `j_t` has no information about `nu_t m_{j_t}` (the replica is pseudo-random), and any `mu' != mu`
passes with probability 1/p over the secret alpha; `nu_t` is never 0. Why not int8 tensor cores (the
compute-as-proof suggestion): unnecessary on H100/B200 at 1.5 ops/byte (the INT pipe is 3x under-subscribed);
the option remains for GPUs with a worse ops/byte ratio.

**Second aggregate for the Merkle-only variant: per-sector keyed universal fingerprint** `h_t = sum_c b_c
(sum_{w<8} a_w m_{c,w}) mod p` (a_w 28-bit, b_c 61-bit, both nonce-derived), one 8-byte value per challenged
sector. Needed only if the verifier holds no tags (then it audits a random subset of the returned `h_t`
against opened sectors; detection is probabilistic per challenge, see protocol2.md).

**Baselines in the same run:** D2D memcpy of X bytes (2X traffic), a sequential streaming-read kernel over X
bytes, and the same random-sector access pattern with an XOR fold only (the random-read ceiling).

**Who computes the tags (the v2 twist).** Tag generation needs the secret `(alpha, k)` and every byte of
`R`; the prover must not have the key and the verifier must not learn `D`. `R` is pseudo-random without the
seed (each stored label is `R_{l-2}[i] XOR PRF_seed(layer, blk, i, parents)`), so the party that computes
the tags may see `R` *if it never sees the seed*. Protocol consequence (protocol2.md): seed issued by the
remote verifier V after `comm_D`; tags computed by the on-node challenger device C from a one-time stream
of `R` at admission (80 GB over PCIe, ~2-3 s at the measured H2D rate); C never receives the seed, V never
receives `R` or the tags. Caveat for the kernel agents: the phase-1 `replica_seed` is a 32-bit constant;
a secret-keyed replica needs a >= 128-bit seed mixed into the state init (`porep/params.py`, not my file).

## 2026-09-03 08:45 -- Kernels correct; random-sector MAC at 98 % of sequential-read bandwidth

`python porep/bench/challenge_bench.py test`: `sw` (wpt 4/8, grids 7/64/300, sectors 4/8/32 KB), `fp`, `xor`
bit-exact against the NumPy reference; the verifier accepts the honest `mu`, rejects a flipped bit and a
prover that substitutes another sector for a missing one (`results/phase2/rq5/` has no CSV for this; the
output is in the log of this entry). NumPy tagging of 64 MB takes ~2 s (8-15 M words/s; a C implementation
is ~100x faster, see cost section).

`bw` sweep (`bw.csv`, region 70 GB of pseudo-random bytes, median of 7, event-timed, back-to-back launches):

| X | memcpy D2D (2X traffic) | seq read | random xor 4 KB | xor 8 KB | xor 16 KB | xor 32 KB | xor 64 KB |
|---|---|---|---|---|---|---|---|
| 1.6 GB | 1.060 ms = 3020 GB/s traffic | 0.508 ms, 3147 GB/s | 0.555 ms, 2881 | 0.524 ms, 3051 | 0.516 ms, 3102 | 0.511 ms, 3131 | 0.507 ms, 3154 |
| 4 GB | 2.634 ms = 3038 | 1.260 ms, 3175 | 1.371 ms, 2918 | 1.290 ms, 3101 | 1.275 ms, 3138 | 1.265 ms, 3162 | 1.253 ms, 3193 |
| 8 GB | 5.256 ms = 3044 | 2.516 ms, 3179 | 2.725 ms, 2935 | 2.560 ms, 3125 | 2.535 ms, 3155 | 2.518 ms, 3177 | 2.499 ms, 3201 |

S-W MAC kernel (`sw`), best grid/wpt per sector size (grid in CTAs/SM; 1 CTA of 1024 threads per SM at 32 KB):

| X | sw 4 KB (grid 4, wpt 4) | sw 8 KB (grid 4, wpt 8) | sw 16 KB (grid 2, wpt 8) | sw 32 KB (grid 1, wpt 8) | fp 32 KB (grid 4) |
|---|---|---|---|---|---|
| 1.6 GB | 0.619 ms, 2585 GB/s | 0.549 ms, 2915 | 0.538 ms, 2976 | 0.530 ms, 3021 | 0.851 ms, 1879 |
| 4 GB | 1.495 ms, 2676 | 1.320 ms, 3029 | 1.305 ms, 3064 | 1.294 ms, 3092 | 2.124 ms, 1883 |
| 8 GB | 2.950 ms, 2712 | 2.600 ms, 3077 | 2.580 ms, 3101 | 2.561 ms, 3124 | 4.221 ms, 1895 |

Reading: (1) the position-wise MAC costs nothing measurable over the raw random read at >= 8 KB sectors
(3.03-3.12 TB/s = 95-98 % of the 3.18 TB/s sequential-read ceiling, 93 % of the 3.35 TB/s spec); 32 KB
sectors reach **3.09-3.12 TB/s = 97-98 % of sequential read** -- the ">= 90 % of memcpy" target is met.
(2) 4 KB random sectors lose 8 % in the raw read (DRAM row locality) and 15 % with the MAC (4 KB sectors
mean 128-thread CTAs, 8/SM, and more per-sector overhead per byte); 8 KB is already within 2 % of the
ceiling. (3) The per-sector fingerprint `fp` (CTA-wide reduction per 32 KB sector, `__syncthreads`) runs at
1.9 TB/s = 60 % -- fine for an audit-based fallback, not for the primary challenge; a warp-per-sector
version would fix it but was not a priority. (4) Grid choice matters for small sectors (1 CTA/SM at 4 KB
gives 1.1 TB/s: too few loads in flight); the driver picks 4/4/2/1 CTAs per SM for 4/8/16/32 KB.
(5) X does not change GB/s between 1.6 and 8 GB: 1.6 GB is already 500 us, far above launch/ramp effects.

Consequence for the deadline: honest read time `T = X / 3.1 TB/s` = 0.52 / 1.29 / 2.56 ms for X = 1.6 / 4 / 8 GB
(back-to-back, warm clocks). Poisson-launched single challenges on an otherwise idle GPU are slower (next entry).

## 2026-09-03 09:00 -- Idle-GPU latency distributions (2000 Poisson challenges per config, 20/s)

`challenge_runs.sh idle` -> `lat_raw_idle.csv`, `lat_summary.csv`. Region 70 GB. Each challenge: a fresh
nonce, host launches `sw` + reduce on a dedicated stream and blocks on an event; `kern` = event time on the
GPU (kernel-only), `host` = wall time from launch to the host observing completion (Python + driver + sync
path; a hardware challenger would see the doorbell-to-mailbox time instead, ~5 us, *plus* whatever the
GPU's own scheduler adds before the kernel starts -- that part is inside `kern` only when the challenger
shares the context, see the in-process runs). Mean gap 50 ms (exponential), so the GPU is idle between
challenges (clocks stayed at 1980 MHz per nvidia-smi).

| S | X | kern p50 | p99 | p99.9 | max | p99.9 - p50 | host p50 | host p99.9 | host max |
|---|---|---|---|---|---|---|---|---|---|
| 32 KB | 1.6 GB | 0.547 | 0.612 | 0.671 | 0.680 | 0.124 | 0.599 | 1.944 | 2.783 |
| 32 KB | 4 GB | 1.314 | 1.377 | 1.445 | 1.517 | 0.130 | 1.367 | 2.017 | 3.571 |
| 32 KB | 8 GB | 2.590 | 2.654 | 2.681 | 2.695 | 0.091 | 2.644 | 2.861 | 2.868 |
| 4 KB | 1.6 GB | 0.635 | 0.699 | 0.731 | 0.839 | 0.096 | 0.689 | 1.532 | 4.893 |
| 4 KB | 4 GB | 1.509 | 1.569 | 1.709 | 1.710 | 0.200 | 1.562 | 2.134 | 2.237 |
| 4 KB | 8 GB | 2.962 | 3.024 | 3.234 | 3.902 | 0.272 | 3.016 | 3.700 | 3.955 |

(ms; n = 2000 each; p99.9 is the 2nd-largest sample.) Reading: an isolated 4 GB challenge takes 1.31 ms
(3.04 TB/s; 2 % slower than back-to-back: cold TLB/L2 state), and the **kernel-side jitter on an idle GPU is
0.09-0.13 ms at p99.9** for 32 KB sectors (0.1-0.27 ms at 4 KB). The host-observed tail is ~0.5 ms worse
(p50 overhead 53 us, p99.9 0.53 ms, max 4.2 ms: Python/OS scheduling; irrelevant for a hardware
challenger, relevant if the on-node agent is a user-space process). Under the plan's 0.3 ms slack the idle
GPU passes with margin; the load-dependent tail is next.

## 2026-09-03 09:25 -- Under decode load, separate process (time-slicing): the GPU scheduler is the jitter

`challenge_runs.sh sep sepplain --load model --w-mode plain --B 16 --ctx 512`: `challenge_load.py` runs
Qwen2.5-7B decode steps (plaintext weights, B = 16, ctx 512, one CUDA graph per step, one step in flight,
8.61 ms/step = 1.64 TB/s of weight reads alone, i.e. the load is HBM-bound at ~55-60 % of the pipe) in its
own process; the challenger runs in a second process with a 54 GB region (the model takes ~16 GB). No MPS
on the pod, so the two contexts are **time-sliced**. Results (`lat_raw_sepplain.csv`, `load_sepplain.csv`,
join in `challenge_analyze.py`):

| S | X | kern p50 | kern p99.9 | kern max | host p50 | host p99 | host p99.9 | host max | load step overlapping a challenge (p50 / p99) vs not (8.61 / 8.63) | load loss at 20/s |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 KB | 1.6 GB | 0.572 | 0.585 | 0.586 | 1.829 | 2.915 | 3.145 | 6.73 | 9.58 / 10.59 | 1.8 % |
| 32 KB | 4 GB | 1.355 | 1.378 | 1.379 | 2.619 | 3.697 | 3.769 | 3.79 | 10.37 / 12.16 | 3.2 % |
| 32 KB | 8 GB | **5.097** | 5.215 | 5.216 | 5.985 | 7.471 | 7.548 | 7.56 | 11.94 / 14.65 | 5.9 % |
| 4 KB | 1.6 GB | 0.630 | 0.640 | 0.644 | 1.927 | 2.979 | 3.201 | 5.52 | 9.64 / 10.70 | 1.9 % |
| 4 KB | 4 GB | 1.510 | 1.525 | 1.525 | 2.757 | 3.831 | 3.893 | 3.95 | 10.52 / 12.45 | 3.6 % |
| 4 KB | 8 GB | 5.446 | 5.518 | 5.518 | 6.352 | 7.802 | 7.881 | 7.92 | 12.31 / 14.98 | 6.3 % |

(ms; n = 2000 per row.) Three things, all consequences of time-slicing:

1. **The kernel itself is undisturbed when it fits in a time slice.** `kern` p99.9 - p50 is 8-23 us for
   X <= 4 GB (tighter than idle, since the challenger's context owns the whole GPU while it runs). The
   8 GB kernel (2.6 ms) does *not* fit: p50 = 5.10 ms = 2.6 ms of work + one full slice of the load
   (~2.5 ms), consistently -- the inter-context slice on this driver is evidently ~2.5 ms, and a kernel
   longer than that is preempted exactly once.
2. **The wait for the slice is the jitter.** host - kern: p50 1.26 ms, p99.9 2.4-2.6 ms, for every X -- the
   challenger's work arrives at a uniformly random point of the load's ~2.5 ms slice and runs at the next
   switch (mean 1.25 ms, max 2.5 ms) plus ~0.1-0.2 ms of switch cost. This is not Python overhead (the idle
   host tail was 0.5 ms); a hardware challenger doorbelling a separate context would see the same 0-2.5 ms.
   **Deadline slack needed under time-slicing: ~2.5 ms** at any X (with the deadline at the observed host
   p99.9: 3.1 / 3.8 / 7.5 ms vs `T` = 0.55 / 1.31 / 2.6 ms). That is 8x the plan's 0.3 ms, and it
   inflates `eps_max` by `(1 + 2.5/T)` = 5.5x at 1.6 GB, 2.9x at 4 GB, 2x at 8 GB.
3. **Load cost**: a load step that overlaps a challenge is longer by ~1.0 / 1.8 / 3.3 ms (kernel + ~0.4-0.7
   ms of two context switches); throughput loss 1.8 / 3.2 / 5.9 % at 20 challenges/s, i.e. ~1.2-1.6x the
   challenger's own HBM time (1.1 / 2.7 / 9.3 % of wall time at this deliberately high rate). At the
   protocol rate of 5/s: 0.5-1.5 %.

Verdict for the separate-process deployment: **fails the 0.3 ms criterion**, not because of HBM contention
(the kernel is as fast as idle) but because of the GPU's inter-context time-slice scheduler. Fixes, in order
of preference: (a) the challenge kernel is launched inside the serving process on a high-priority stream
(measured next; it is an "agent kernel" already in the plan), (b) MPS (contexts share one scheduler, the
challenger's CTAs interleave; not available on this pod), (c) accept a 2.5 ms slack and pay 2-5x in `eps`.

## 2026-09-03 09:50 -- Under decode load, same process, high-priority stream: p99.9 - p50 = 0.32-0.37 ms

`challenge_runs.sh inproc inprocP_S32 high 32 1 8 --load-wmode plain`: the same Qwen decode step (CUDA
graph) replayed on a lowest-priority stream, kept 4 steps deep so the GPU never idles; the challenger on the
highest-priority stream (`cudaStreamCreateWithPriority`, -3) in the same process; `kern` = event pair on the
challenger stream, which now includes the wait for SM resources (the event is recorded the moment the stream
reaches it, the kernel starts when the CTA scheduler finds room). `lat_raw_inprocP_S32.csv`:

| S | X | kern min | p50 | p90 | p99 | p99.9 | max | p99.9 - p50 | p99.9 - idle p50 | load step p50 / p99 (steps hit by 0/1/2 challenges) |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 KB | 1.6 GB | 0.527 | 0.579 | 0.654 | 0.837 | 0.925 | 0.944 | 0.35 | 0.38 | 9.09 / 10.05 |
| 32 KB | 4 GB | 1.292 | 1.357 | 1.424 | 1.619 | 1.681 | 1.689 | 0.32 | 0.37 | 9.09 / 11.59 |
| 32 KB | 8 GB | 2.561 | 2.635 | 2.696 | 2.869 | 3.005 | 3.008 | 0.37 | 0.42 | 9.09 / 14.12 |

(ms; n = 2000.) Histogram of `kern - min` (4 GB row): 0-0.15 ms: 96 %; 0.15-0.2: 1.5 %; 0.2-0.4 ms: 2.5 %;
above 0.4: 0. The shape is the same for every X: **an additive wait of 0-0.15 ms most of the time and a
0.2-0.45 ms wait 2-3 % of the time**, independent of X, i.e. it is the time for the load's resident CTAs to
drain from the SMs (the 1024-thread MAC CTA uses 54 registers per thread = 87 % of the SM's register file
(`cuobjdump --dump-resource-usage`): it cannot co-reside with a GEMM CTA, so each SM must finish its current
load CTAs first; a few kernels of the decode step -- attention
and the largest GEMMs -- have CTAs living 0.2-0.4 ms). Once resident the challenger owns the SMs and reads at
the idle rate (min = idle min), and the load is stalled for exactly the challenge duration: load steps hit
by one challenge are longer by `T`, by two challenges by `2T` (the p99 column: 9.09 + 2 x 0.58 / 1.36 / 2.6).
The 9.09 ms p50 is the load alone in this harness (`base_plain`: 9.09 ms at 2 challenges/s; the 8.61 ms of
the separate-process run had a host sync gap between steps). Load cost per challenge = `T`, nothing more; at
5/s and 4 GB that is 0.68 % of throughput.

Against the plan's criterion (p99.9 jitter <= ~0.3 ms at <= 1 % HBM time): **0.32-0.37 ms**, marginally
above 0.3, flat in X. With the deadline set at the measured under-load p99.9 plus 0.1 ms margin, the
slack over the idle honest time is 0.48 / 0.47 / 0.52 ms for X = 1.6 / 4 / 8 GB, so `(1 + slack/T)` =
1.88 / 1.36 / 1.20. That factor multiplies every tier residual (tier entry below), which is the argument
for the largest X the HBM budget allows: 8 GB at <= 3.8/s or 4 GB at <= 7.6/s stay within 1 % of HBM time
(5 x 2.6 ms = 1.3 % for 8 GB at 5/s).

**Stream priority has no measurable effect** (`inprocD_S32`, same run with the challenger on a default-
priority stream): kern p99.9 = 0.927 / 1.690 / 2.972 ms vs 0.925 / 1.681 / 3.005 with priority -3; p50 and
load cost identical. The wait is for SM resources to free up, and once a load CTA retires the pending
challenger CTA gets the slot either way (the load's graph has only one kernel's CTAs pending at a time, and
the dispatcher evidently does not starve the second stream). Priority would matter with several competing
streams; it does not buy anything against a single serving stream.

## 2026-09-03 10:15 -- The v2 load: with the phase-1 *encoded-weights* decode as the load, p99.9 jitter is 1.6-1.8 ms

`inprocP_S32fused`: same as above but the Qwen step runs with PoRep-encoded weights (`w_mode fused`, the
phase-1 fused decode + GEMV path; 40.8 ms/step = 4.5x plaintext, phase-1 numbers). This is the actual v2
deployment (the weights *are* encoded), and the challenger tail changes completely (`lat_raw_inprocP_S32fused.csv`):

| X | kern p50 | p99 | p99.9 | max | p99.9 - idle p50 | load step p50 / p99 |
|---|---|---|---|---|---|---|
| 1.6 GB | 0.716 | 2.231 | 2.523 | **5.667** | 1.98 | 40.76 / 42.30 |
| 4 GB | 1.483 | 2.680 | 3.284 | 3.297 | 1.97 | 41.52 / 44.23 |
| 8 GB | 2.769 | 3.947 | 4.404 | 4.450 | 1.81 | 42.79 / 48.36 |

Even the p50 moves (+0.14-0.17 ms) and p99 is 1.2-1.5 ms over idle. Cause, from `porep/kernels/porep_kernels.cu`:
the phase-1 decode and fused-GEMV kernels are **persistent-CTA** kernels (`grid = min(nblocks, 132 x 4)`, each
CTA loops `for (j = blockIdx.x; j < nblocks; j += gridDim.x)` with 128-227 KB of dynamic shared memory), so a
CTA lives as long as its kernel: 0.3-1 ms for a 135 MB MLP matrix, ~3 ms for the 1.09 GB `lm_head` at the
0.35 TB/s effective decode rate. The challenger's CTAs cannot start on an SM until that SM's decode CTA
exits, and the SMs free up in a staggered way, so the challenger also runs the first part of its read at
partial occupancy (the p50 shift). The 5.7 ms maximum is a challenge that landed at the start of the
`lm_head` decode. **Under the phase-1 decode kernels the pass criterion fails by 5-6x**, with the plaintext
model it fails by 1.1-1.2x, and the difference is entirely the CTA lifetime of the load's kernels.

What this means for the design (RQ1/RQ2 kernel agents, not this RQ's code): the serving process's kernels
need **bounded CTA lifetime** (<= ~50 us) or a **yield flag**. (a) Non-persistent grids: `grid = nblocks`
(one 64 KB block per CTA, ~10-40 us of work) instead of `min(nblocks, 528)`; the launch cost of 16 k CTAs is
negligible against 3 ms. Tested below with the synthetic load (`decode_grid`). (b) Persistent CTAs that poll
a device flag between blocks and exit when the challenger raises it, with work claimed from a global counter
so a re-launch finishes the remainder: ~20 us of reaction time, no throughput cost when no challenge is
pending. (c) Leave room: if the decode kernel used <= half the register file and shared memory per SM, a
half-size challenger CTA could co-reside and start immediately, at the price of sharing issue slots with an
INT-bound kernel (measured next with 4 KB / 16 KB sectors = 128- / 512-thread CTAs).

(c) does not work (`inprocP_S4fused`, 4 KB sectors = 128-thread CTAs, 4 per SM, which *can* co-reside with
a 512-thread decode CTA): kern p50 0.898 / 1.778 / 3.231 ms (idle: 0.635 / 1.509 / 2.962 -- the co-resident
challenger shares the SM's issue slots and load queues with the INT-bound decode CTA and runs 15-40 %
slower), p99.9 2.157 / 3.694 / 6.290 ms. Co-residency trades the drain wait for a slower read and keeps the
tail (the decode CTA's shared memory -- 64 KB block + staging -- still blocks part of the SM). The fix has to
be on the load side ((a) or (b)).

Nor do 16 KB sectors (`inprocP_S16fused`, 512-thread CTAs, 2 per SM): p50 0.725 / 1.497, p99.9 2.247 /
2.933 ms at X = 1.6 / 4 GB -- indistinguishable from the 32 KB configuration.

The same 4 KB / 128-thread configuration under the *plaintext* model load (`inprocP_S4`) shows the other
face of co-residency: kern p50 1.206 / 2.922 ms at X = 1.6 / 4 GB (idle 0.635 / 1.509; p99.9 1.697 /
3.484) -- the co-resident challenger shares HBM bandwidth with the GEMMs (which are themselves HBM-bound at
~1.6 TB/s) and gets roughly half of it, while the load is barely slowed (9.10 vs 9.09 ms). A challenger
whose median depends on the load's intensity cannot have a fixed deadline. **Design rule: the challenge
kernel must take the SMs exclusively** (the 1024-thread CTA of the 32 KB configuration, 87 % of the register file,
does exactly that) so that its read runs at the idle rate and the load pays exactly `T` per challenge.

## 2026-09-03 10:45 -- Confirming the mechanism with the synthetic load: persistent vs one-block CTAs

`inprocP_S32synP`: load = phase-1 decode of a 1 GB encoded buffer (`grid = min(nblocks, 528)`, persistent
CTAs, the kernel runs ~2 ms) + 8 bf16 GEMMs `[16 x 8192 x 8192]`, 2.62 ms/step; challenger 32 KB, X = 4 GB:
kern **p50 2.066**, p99 3.254, p99.9 3.298, max 3.299 ms (idle p50 1.314). The median waits ~0.75 ms and the
tail waits a full ~2 ms: the challenge lands at a uniformly random point of the decode kernel and has to wait
for its persistent CTAs to finish. `inprocP_S32synS`: identical load with `decode_grid = nblocks` (16384
one-block CTAs, ~20-40 us each): kern **p50 1.409, p99 1.451, p99.9 1.493, max 1.602 ms** (idle 1.314 /
1.377 / 1.445 / 1.517); the load step is unchanged (2.58 vs 2.62 ms, one-block CTAs cost nothing).

| load (X = 4 GB, 32 KB sectors, same process) | kern p50 | p99 | p99.9 | max | p99.9 - idle p50 |
|---|---|---|---|---|---|
| none (idle GPU) | 1.314 | 1.377 | 1.445 | 1.517 | 0.13 |
| synthetic, decode kernel with **persistent** CTAs (phase-1 default) | 2.066 | 3.254 | 3.299 | 3.299 | 1.98 |
| synthetic, decode kernel with **one-block** CTAs (`grid = nblocks`) | 1.409 | 1.451 | 1.493 | 1.602 | **0.18** |
| Qwen decode step, plaintext weights (cuBLAS / attention kernels) | 1.357 | 1.619 | 1.681 | 1.689 | 0.37 |
| Qwen decode step, phase-1 encoded weights (persistent decode CTAs) | 1.483 | 2.680 | 3.284 | 3.297 | 1.97 |

So the jitter is a property of the load's kernels, and it is controllable: with bounded CTA lifetime the
challenge kernel's p99.9 is within 0.18 ms of the idle median -- **inside the 0.3 ms criterion** -- and the
plaintext model's 0.37 ms comes from a few library kernels (attention, the largest GEMMs) whose CTAs live
0.2-0.4 ms; a serving stack that wants a tight deadline would split those too (split-K / smaller tiles), or
accept 0.4-0.5 ms of slack. Recommendation to the RQ1/RQ2 kernel agents: `grid = nblocks` (or a yield flag)
for decode and fused GEMV kernels; the phase-1 `porep_kernels.cu` launch sites are `min(nblocks, 132 x 4)`.

## 2026-09-03 12:05 -- The fix on the real v2 load: encoded-weights Qwen step with one-CTA-per-block decode

`inprocP_S32fusedB` (`--load-bounded-ctas`: `challenge_load.py` monkeypatches `PoRepCodec.decode` to pass
`grid = nblocks` for whole-buffer decodes; `porep/cuda.py` itself untouched). Same encoded-weights Qwen load
as the 10:15 entry (at B = 16 the "fused" mode takes the decode-then-cuBLAS path, so the decode kernel is
the one whose CTAs were persistent):

| X | kern p50 | p99 | p99.9 | max | p99.9 - idle p50 | persistent-CTA (10:15) p50 / p99.9 | load step p50 |
|---|---|---|---|---|---|---|---|
| 1.6 GB | 0.622 | 0.694 | 0.912 | 0.921 | 0.37 | 0.716 / 2.523 | 39.94 (was 40.76) |
| 4 GB | 1.400 | 1.476 | 1.684 | 1.708 | 0.37 | 1.483 / 3.284 | 40.91 (was 41.52) |
| 8 GB | 2.682 | 2.771 | 3.001 | 3.009 | 0.41 | 2.769 / 4.404 | 42.17 (was 42.79) |

The one-line launch change removes the whole excess: the encoded-weights load now has exactly the plaintext
model's tail (0.37-0.41 ms, from the cuBLAS/attention kernels that remain), and the load itself runs 2 %
faster with one-block CTAs. This is the number for the pass criterion on the actual v2 load: **p99.9 = idle
median + 0.37-0.41 ms, i.e. slack 0.5 ms**, at a load cost of exactly `T` per challenge.

## 2026-09-03 11:05 -- Adversary tiers: PCIe host DRAM measured, others from published numbers

`challenge_runs.sh tier` -> `tier.csv` (pod c: H100 SXM on a PCIe Gen5 x16 link (`nvidia-smi`: gen 5,
width 16); a single GPU is visible, so no NVLink peers to measure; `nvidia-smi topo -m` shows NIC0 at `PIX`,
i.e. on the GPU's own PCIe switch, as on an HGX node; 5 reps, event-timed):

| path | X | ms | GB/s |
|---|---|---|---|
| pinned host -> device, copy engine (`cudaMemcpyAsync`) | 1 / 4 GB | 18.0 / 72.0 | **55.5** |
| device -> pinned host, copy engine | 1 / 4 GB | 18.0 / 72.6 | 55.1-55.4 |
| 4096 separate one-sector `cudaMemcpyAsync` (4 / 32 / 64 KB) | 16 / 128 / 256 MB | 13.6 / 15.4 / 18.0 | 1.2 / 8.7 / 15.0 (host-issue bound, ~3.5 us per call) |
| kernel streaming read of *mapped* host memory (zero-copy) | 1 / 4 GB | 19.5 / 77.9 | 51.3 |
| kernel random-sector read of mapped host memory, 4 / 32 / 64 KB sectors (xor fold) | 1 GB | 19.5 | 51.2-51.4 |
| **S-W MAC kernel directly over mapped host memory**, 4 / 32 KB sectors | 1 GB | 19.5 | 51.1-51.3 |
| HBM reference in the same run: seq read / sw 32 KB | 4 GB | 1.26 / 1.33 | 3172 / 3008 |

Reading: (1) the copy engine gets 55.5 GB/s (Gen5 x16 practical maximum is ~56-58 GB/s after protocol
overhead; the measured value is 87 % of the 64 GB/s raw); (2) a kernel reading mapped host memory gets 51 GB/s
**regardless of access pattern** -- random 4 KB sectors are as fast as a sequential stream, because PCIe
reads are 64-256 B transactions anyway; so an adversary that keeps a fraction of the replica in host DRAM
answers a challenge over that fraction *with the same kernel*, at 51 GB/s, no staging needed; (3) issuing one
copy per sector from the host is 4-40x slower and is not what an adversary would do. (4) Since the NIC (RDMA
to a pool or a peer node) hangs off the same PCIe x16 link as the host path on an HGX node (GPUDirect goes
through the GPU's PCIe switch but over the GPU's own x16 link), host DRAM + NIC + NVMe together are bounded
by the one link: **`B_tier,PCIe-attached` = 51-56 GB/s = 1.7-1.8 % of `B_HBM,eff` = 3.04 TB/s**
(`X / T_idle,p50`).

Enforceable `eps_max = B_tier / B_HBM (1 + slack / T)` (`challenge_analyze.py tiers`, T = idle p50):

| tier (B) | X = 1.6 GB, slack 0.5 ms | X = 4 GB, slack 0.5 ms | X = 8 GB, slack 0.5 ms | X = 4 GB, slack 2.5 ms (time-sliced) |
|---|---|---|---|---|
| PCIe-attached (host DRAM, NIC, NVMe): 55.5 GB/s copy engine | 3.5 % | **2.5 %** | 2.2 % | 5.3 % |
| same, kernel over mapped memory: 51.3 GB/s | 3.2 % | 2.3 % | 2.0 % | 4.9 % |
| NVLink4 peer HBM: 450 GB/s one direction (published) | 28 % | 20 % | 18 % | 43 % |
| GB200 (X = 9.3 GB = 5 %, T = 1.25 ms, HBM 7.44 TB/s eff): C2C 450 GB/s (published) | -- | 8.5 % | (X = 10 %: 7.2 %) | -- |
| GB200: Grace LPDDR5X share, 256 GB/s per GPU (published, both GPUs streaming) | -- | 4.8 % | (X = 10 %: 4.1 %) | -- |

The NVLink row is not a per-GPU capacity leak when **all GPUs of the NVLink domain are challenged
simultaneously**: a peer's HBM is fully accounted by its own challenge, so bytes served over NVLink are
bytes missing from the peer, and the node-wide deficit is bounded by the sum of the PCIe-attached tiers
(8 x 55 GB/s vs 8 x 3.04 TB/s: the same 1.8 %). Without simultaneity, an idle peer is a 450 GB/s tier and
the residual is 20 % -- simultaneity is mandatory, and on GB200 the 72-GPU domain must be challenged as one
(Grace's LPDDR is then the binding tier at 4.8 %, or the C2C link at 8.5 % if the host is otherwise idle).

**Challenge rate for detection.** A steady cheater with `eps > eps_max` misses every deadline (`eps X /
B_tier > T + slack` deterministically -- there is no luck in a bandwidth bound), so detection needs one
challenge: with Poisson rate `lambda`, `P(detected within N s) = 1 - exp(-lambda N)`; at 5/s: 99.3 % within
1 s, 99.9999 % within 3 s; with the "5 late of 100" rule, 5 challenges = 1 s. HBM time at 5/s: 0.66 % (4 GB),
1.3 % (8 GB; use 3.8/s for the 1 % budget), 0.27 % (1.6 GB). An *intermittent* cheater that offloads only
for a fraction `f` of the time is detected with `1 - exp(-lambda f N)`: at `f = 10 %`, 5/s: 99.3 % within
10 s; its minimum useful interval is bounded below by the migration cost `2 (eps - eps_max) H / B_tier`
(1.6 GB out and back over PCIe: 58 ms). At 5/s the per-challenge HBM stall is 1.3 ms once per 200 ms:
+0.66 % on decode latency, invisible at the token level.

## 2026-09-03 11:30 -- Regeneration latency measured (dedication bound, protocol2.md Section 5)

`challenge_regen.py` -> `regen.csv`: the phase-1 encode kernel on buffers of 1 ... 16384 blocks (the kernel
runs one block's chain per thread group, so 1 block = one sequential labeling chain), 9 reps, event-timed:

| params | block | encode 1 block (= chain latency) | ns / node | encode 132 blocks | encode 16384 blocks | decode 1 block | decode 16384 blocks |
|---|---|---|---|---|---|---|---|
| l=3, d=4, r=3, n=2048 | 64 KB | **3.61 ms** | 588 | 3.61 ms | 169 ms = 6.3 GB/s | 30 us | 2.24 ms = 480 GB/s |
| l=3, d=4, r=3, n=4096 | 128 KB | **7.21 ms** | 586 | 7.21 ms | 885 ms = 2.4 GB/s | 47 us | 5.5 ms = 388 GB/s |
| l=2, d=4, r=3, n=2048 | 64 KB | 2.43 ms | 593 | 2.43 ms | 114 ms = 9.4 GB/s | 22 us | 1.59 ms = 675 GB/s |
| l=3, d=4, r=2, n=2048 | 64 KB | 3.30 ms | 537 | 3.30 ms | 155 ms = 6.9 GB/s | 26 us | 2.09 ms = 514 GB/s |

The chain time is `l x n x 0.59 us` (my protocol draft had assumed 0.33 us; the measured mixer is 1.8x
slower per node, which *helps* the dedication bound): an adversary holding only `D` and the seed cannot
produce any sector of a 64 KB block in less than 3.6 ms, vs. a deadline of `T + 0.5 ms` = 1.81 ms at X = 4 GB
(2.0x margin) or 3.09 ms at X = 8 GB (1.17x: too thin -> 128 KB blocks, 7.2 ms, 2.3x). RQ1's faster mixers
would shrink these proportionally; the rule `l n t_hash >= 2 (T + slack)` goes into the parameter table.
Side results: the phase-1 encoder is latency-bound (6.3 GB/s at l=3, saturating at ~16 CTAs/SM; ~13 s for an
80 GB admission), single-block decode is 30 us (consistency-opening cones are cheap), and bulk decode is
0.48 TB/s at l=3 -- the rate that made the encoded-weights Qwen step 4.5x slower than plaintext above.

## 2026-09-03 20:30 -- Final: the merged phase-2 kernels at the security point, every CTA-lifetime mode

Coordinator follow-up. Merged `p2/k2` (contains `p2/k1`: ping-pong decode kernel with bounded CTAs
`POREP_BPC=2` default, 128-bit `replica_key`; K2's fused decode->WGMMA `fusedmm` path with
`POREP_FUSED_BPC=autoN`) into `p2/p1` -- no conflicts (my code is under `porep/challenge/` and
`porep/bench/challenge_*`), `tests/test_porep.py`, `tests/test_fused.py` and `challenge_bench.py test` pass on
pod c after the rebuild. W1 is finished, so the GPU was mine (no lock contention; `nvidia-smi` showed 0 MiB
before the runs). Load = Qwen2.5-7B, B = 16, ctx 512, weights encoded at the security point
`PoRepParams(chunk_bytes=32, n_chunks=1024, layers=4, degree=6, rounds=3, mixer=1, parent_sampler="dru")`
(32 KB blocks, K1's kernels2.md), in the same process on the default stream with 4 steps queued; challenger
on its own high-priority stream, `sw` MAC, X = 4 GB, 32 KB sectors, 1 CTA/SM x 1024 threads, 2000 Poisson
challenges at 5/s (400 s per mode, ~10.5-11.5 k load steps overlapped per mode). Script
`porep/bench/challenge_final.sh`; rows in `jitter_final.csv`, per-challenge rows in `lat_raw_final_*.csv`.
Idle reference in the same session and at the same rate (n = 1000): p50 1.324 / p99 1.410 / p99.9 1.585 ms
(the 5/s cadence lets the clocks drop between challenges: p50 +0.01 ms and a few ramp outliers vs the 20/s
idle run's 1.314 / 1.377 / 1.445).

| load mode (kernel knobs) | kern p50 | p99 | p99.9 | max | **p99.9 - idle p50** | load step p50 / p99 (ms) | verdict |
|---|---|---|---|---|---|---|---|
| unfused, ping-pong + `POREP_BPC=2` (K1 default) | 1.404 | 1.474 | 1.662 | 1.753 | **0.34** | 38.09 / 40.66 | pass (0.5 ms slack) |
| unfused, `POREP_BPC=0` (persistent grid) | 1.491 | 2.781 | 3.147 | 3.152 | **1.82** | 38.12 / 40.69 | fail |
| `fusedmm`, `POREP_FUSED_BPC=0` (K2 default, persistent) | 1.499 | 3.390 | 3.724 | 3.752 | **2.40** | 35.21 / 37.67 | fail |
| `fusedmm`, `POREP_FUSED_BPC=auto4` | 1.375 | 1.437 | 1.494 | 1.707 | **0.17** | 35.55 / 37.66 (+1.0 %) | pass (0.3 ms slack) |
| `fusedmm`, `POREP_FUSED_BPC=auto2` | 1.353 | 1.415 | 1.435 | 1.465 | **0.11** | 35.64 / 37.63 (+1.2 %) | pass |
| plaintext Qwen step (reference) | 1.362 | 1.613 | 1.703 | 1.727 | **0.38** | 9.09 / 10.36 | marginal |
| idle (no load, same session) | 1.324 | 1.410 | 1.585 | 1.585 | 0.26 | -- | -- |

Reading. (1) **Bounded CTAs do what the 12:05 entry predicted, on both kernels.** The persistent variants
put p99.9 at 3.1-3.7 ms (excess 1.8-2.4 ms; the fused persistent kernel is worse than the unfused one
because its lm_head launch lives ~2.6 ms per CTA, fused2.md) -- 4-5x over the 0.5 ms slack. Bounding
brings the excess to 0.34 ms (unfused, ~16-41 us CTAs) and 0.11-0.17 ms (fused, ~45-90 us CTAs). (2) The
fused bounded modes have a *smaller* tail than the plaintext model (0.38 ms): at l = 4 the encoded step is
92-94 % fused-decode kernel, whose CTAs are now bounded, so the cuBLAS/attention kernels that set the
plaintext tail (some with 0.3-0.4 ms CTAs) are a smaller share of the timeline. The unfused mode still has
the plaintext GEMMs in it, hence 0.34 ~ plaintext. (3) Bounding costs nothing measurable in the unfused
kernel (38.09 vs 38.12 ms; K1: -1.5 to +2 %) and +1.0 % (`auto4`) / +1.2 % (`auto2`) in the fused kernel
here (K2 measured +3.4 % / +8.5 % in isolated e2e; the difference is within the run-to-run spread of the
step time at 5/s challenge cadence, where each challenge stalls the load for ~1.4 ms = 0.7 % of the
timeline in every mode). (4) Under-load p50 is +0.03-0.08 ms over idle in the bounded modes (the challenger
waits for the last <= 90 us of resident CTAs on each SM) and +0.17 ms in the persistent modes. (5) The load's
step time is 35.2-35.6 ms fused / 38.1 ms unfused vs 9.09 plaintext = 3.9x / 4.2x -- K2's and K1's e2e
numbers (35.3 / 38.2 ms) reproduce within 1 %.

**Pass criterion (p99.9 - idle p50 <= 0.3-0.5 ms): holds in all three bounded modes** (0.34 unfused,
0.17 `auto4`, 0.11 `auto2`), fails in both persistent modes (1.8 / 2.4 ms). **Recommended shipping default:
`fusedmm` with `POREP_FUSED_BPC=auto4`** -- it is the fastest decode path (35.5 ms vs 38.1 unfused), its
tail (0.17 ms) fits a 0.3 ms slack with margin, and it costs ~1 % (K2: 3.4 %) over persistent; `auto2`
buys 0.06 ms of tail for another ~0-5 % and is not needed at 0.3 ms slack. The unfused default (`POREP_BPC=2`,
ping-pong) is fine at 0.5 ms slack. K2's persistent default (`POREP_FUSED_BPC=0`) must not ship. Deadline
recommendation stays `T + 0.5 ms` for an unfused/plaintext-heavy stack and can be `T + 0.3 ms` when the whole
serving stack is `fusedmm auto4` + bounded attention.

**Regeneration at the security point (`challenge_regen.py --out regen_final.csv`, K1's merged encoder,
1-block buffers = one sequential chain):**

| params | block | chain (encode 1 block) | ns / node | encode 2112 blocks | decode 1 block | decode 2112 blocks |
|---|---|---|---|---|---|---|
| (4,6,3) drU mixer 1, n=1024 (**security point**) | 32 KB | **1.61 ms** | 392 | 6.8 ms = 10.2 GB/s | 24 us | 0.155 ms = 445 GB/s |
| (4,6,3) drU mixer 1, n=2048 | 64 KB | **3.16 ms** | 385 | 19.8 ms = 7.0 GB/s | 30 us | 0.33 ms = 422 GB/s |
| (4,6,4) drU mixer 1, n=1024 | 32 KB | 1.89 ms | 461 | 7.8 ms = 8.9 GB/s | 24 us | 0.166 ms = 416 GB/s |
| (2,6,3) distinct mixer 1, n=1024 | 32 KB | 0.83 ms | 405 | 3.7 ms = 18.6 GB/s | 15 us | 0.084 ms = 827 GB/s |

Mixer 1 is 1.5x faster per node than mixer 0 (392 vs 588 ns) and the block halved, so the chain of the
security point is **1.61 ms < 1.81 ms deadline (0.89x)**: the dedication latency bound of protocol2.md
Section 5 does *not* hold at 32 KB blocks and X = 4 GB -- an adversary that stores nothing for `D = 0`
filler blocks can regenerate the challenged ones inside the window, and only the work bound (whole-GPU INT
pipe, ~2.4 ms for 4 GB at K1's 1.7 TB/s ALU floor, i.e. eps up to ~50-75 %) remains. 64 KB blocks restore
1.75x (3.16 ms; 1.96x with 0.3 ms slack); X = 1.6 GB keeps 32 KB blocks at 1.53x (deadline 1.05 ms) at the
price of `eps_max` 3.5 %; r = 4 does not help (1.04x). The 392 ns is the K1 encoder's dependent-chain
latency per node and is an *upper* bound on an optimised adversary's chain, so 2x is the floor of the rule.
Spec updated (Section 2, 5, 8, one-screen summary): **block >= 64 KB (`l n >= 8192` nodes) at X = 4 GB**;
this costs K2's path +6 % e2e (37.5 vs 35.3 ms at B = 16 with 64 KB fusedmm). The coordinator / RQ3 owners
should decide between 64 KB blocks and X = 1.6 GB; I recommend 64 KB.

**128-bit key vs the spec.** K1's change carries the key as four 32-bit words XORed into hash state words
3..6: `replica_seed` (k0, 32-bit int) + `replica_key` (k1..k3, <= 24 hex digits = 96 bits). The spec's
`seed = PRF_K_seed(gpu, store, slot, epoch, comm_D)` maps onto it as `(replica_seed | replica_key) =
split_32|96(seed)`: all 128 bits secret, replica-id separation inside the PRF input (K1 documents k0 as
"public-ish domain separation"; in this protocol it is the low word of the secret). The spec text in
Section 2 and the admission listing now say so; two notes recorded there: an implementation that leaves
`replica_seed` at the default has a 96-bit secret (acceptable but not to spec), and words 4..6 are IV
constants in the unkeyed ChaCha-style design, so S2 should sign off the keyed initial state (K1 asked the
same). Nothing else in the protocol changes (`Enc_seed`, openings, re-keying all read "seed" as the 128-bit
value; `tag()` never leaks the key).

Pod hygiene: nothing left running; `results/phase2/rq5/` on the pod holds all CSVs + `.cmd` sidecars,
pulled to `results/pod-c/phase2/rq5/`; `jitter_final.csv` / `regen_final.csv` also copied to
`results/phase2/rq5/` in the worktree.
