# Lane enc-hopper — B-Ligero encode + Merkle on the H100 (protocol-identical)

CHECKPOINT 0da4b1b (lane/enc-hopper, 6 commits on main 6babe27; 10:50Z) — mergeable: everything below plus **0da4b1b:
the encoder generalised to n/l ∈ {2, 4, 8}** (`NC` cosets; the staged store writes each position's NC values as one
8- / 16- / two 16-byte stores; `protocol._simt_encoder` now picks the SIMT kernel at n = 2 l / 8 l too — main fell back
to the torch NTT there: 25.5 / 81.4 ms vs **0.97 / 3.56 ms** per 3328-row sub-batch at l=16384; n = 4 l expands to the
15d370e code, 1.73 ms). Validation run **r20260923-101926-dcdc** (0da4b1b vs main 6babe27): 62/62 files identical,
pytest rc=0, `encode_simt_test` PASS at (l, n/l) ∈ {256,4096,8192,16384}×4 ∪ {4096,16384}×{2,8}, Rust ACCEPT on all 8
dump trees, 6 gates rc=0. Snapshot **enc-hopper-v4 = art:81b4248af9a5011b826501fbd777bcb1a42a75a30c59d2b386ece6fdf05e49e4**.
`git merge-base main lane/enc-hopper` = 15d370e at 11:58Z: the coordinator has merged everything up to checkpoint 4;
**0da4b1b is the single unmerged commit** (touches `encode_simt.py`, `encode_simt_test.py`, and 3 lines of
`protocol._simt_encoder`). Checkpoint 4 = 15d370e (5 commits; 09:50Z) — mergeable: `encode_simt.py` (v3 kernel:
radix-16 register stages + 3 swizzled conflict-free smem passes per transform, int64 in-place input, `coefs_out=` int64
view, new `encode_coefs()` for coefficient-form rows, `CF_GLOBAL` variant for parts whose shared memory per block
cannot hold 2·l words — Ada / consumer Blackwell at l=16384, chosen from `sharedMemPerBlockOptin`, and **new in
15d370e: the `STAGE` codeword store** — cosets 0–2 parked coset-major in a per-CTA L2-resident staging buffer, coset 3
reads them back and writes each position's four values as one 16-byte store, every sector written once and complete;
sm_80+ default, `stage=False` keeps the 4-byte evict_last stores), `encode_simt_test.py` (both store paths), new
`commit_gpu.py` + `commit_gpu_test.py` (protocol-specialised Blake3 Merkle, 3 launches), `merkle.py` (uses it,
`commit_device(U, stream=)`), `protocol.py` **ZK encode call site only** (lines 871–889: `torch.empty` + the kernel's
int64 coefficient output + `encode_coefs` for the mask rows instead of `zeros` + int32→int64 copy + torch
`eval_on_coset`). Validation run **r20260923-092554-cc4c** (lane tree at HEAD 15d370e vs /workspace/src-main = main
6babe27, on vy-enc-hopper): pytest `backends/direct/ligero` **68 passed, 1 skipped** (2 v2 deselected); bit-exact with
seeded coins + mask keys **62/62 files identical** over 8 relation/mode pairs (bf16-hopper int-ZK / int-nonZK 10/10
each, fp8-hopper 10/10 each, bf16-ampere vu.py 7/7 each, fp4-nvf4 4/4 each — kernel caches warmed first, §3); Rust
`ligero-verify batch --target-bits 128` ACCEPT on all 8 lane dump trees (python_agree where the run had Python files);
6 gates rc=0. Rust tree identical to main. `git status --short` empty. Earlier validations, all green:
r20260923-085822-cb9f (af3b7de), r20260923-080923-40cf (29dd5b8), r20260923-073018-cb94 (247379e),
r20260923-064515-edd8 (429f8ea). Snapshot **enc-hopper-v3 = art:ee9b62fd80eb445b789e1a213480bcd7abb4d852c64e9e51045b863da51f9613**
(the v2 members + the four 15d370e bench rows + the cp4 validation events).

Author: lane enc-hopper (overnight 2026-09-23). Worktree `~/projects/verity-main-wt/enc-hopper`, branch `lane/enc-hopper`.
Pod `vy-enc-hopper` (runpod de87jjrsjm8pdg, NVIDIA H100 80GB HBM3 SXM, reference part, $3.49/h, created 05:47Z; host
Xeon Platinum 8470, 208 vCPU). Campaign `r21-enc-hopper`. Snapshots **enc-hopper-v3 =
art:ee9b62fd80eb445b789e1a213480bcd7abb4d852c64e9e51045b863da51f9613** (17 bench results + 3 validation event logs;
supersedes enc-hopper-v2 = art:17feca22e1f21f5e9b813b2d7d962e425425b2b9840f7c70dfa377299c841ddd).
Scripts in `evidence/scripts/` (launch.sh / bench.sh / dev.sh / validate2.sh / bitexact_cli.py / enc_v3_*.py / mk_abl.py …).

## 0. Headline (like-for-like on vy-enc-hopper, `bench-vu --batch 16384 --total-vus 4096 --reps 3 --target -128`, median of 3, dumps rep1)

Confirmation rows for the final commit 0da4b1b (n/l-generalised kernel; NC=4 expands to the 15d370e code) after RunPod
moved the pod to a busier host (~10:00Z; same Xeon 8470 model, load avg 7–8 vs ~1 before): bf16-hopper int-ZK
r20260923-104941-5d2f **encode 0.0549 / merkle 0.0193 / encoding_commitment 0.0746 s**, t.total 0.632 (cp4 on the quiet
host: 0.0530 / 0.0191 / 0.0724, 0.588); fp8-hopper int-ZK r20260923-105905-271b **0.0297 / 0.0112 / 0.0412**, t.total
0.531 (cp4: 0.0284 / 0.0105 / 0.0391, 0.369 — the +0.16 s is all host phases). GPU phases within 4–7 % of cp4 = host
noise; the table below (07–09Z, quiet host) stays the like-for-like comparison against main.

| row | tree | run | result art | encode s | merkle s | encode+merkle | t.total s | overhead vs peak |
|---|---|---|---|---|---|---|---|---|
| bf16-hopper int-ZK | main 6babe27 | r20260923-074139-fe6a | art:dd8fa89f… | 0.1105 | 0.0474 | 0.1583 | 0.676 | 5.31e7 |
| bf16-hopper int-ZK | lane 247379e (kernel v3) | r20260923-074052-bb4f | art:7d9c5a88… | 0.0789 | 0.0203 | 0.0996 | 0.634 | 4.98e7 |
| bf16-hopper int-ZK | lane 29dd5b8 | r20260923-080740-9e3d | art:e0f2cd38… | 0.0627 | 0.0194 | 0.0825 (1.92x) | 0.660 | 5.19e7 |
| **bf16-hopper int-ZK** | **lane 15d370e (staged store)** | **r20260923-093805-28f2** | **art:76353c55…** | **0.0530** | **0.0191** | **0.0724 (2.19x)** | 0.588 | 4.62e7 |
| bf16-hopper int-nonZK | main 6babe27 | r20260923-074601-745f | art:8c63cc74… | 0.0853 | 0.0465 | 0.1322 | 0.649 | 5.10e7 |
| bf16-hopper int-nonZK | lane 247379e | r20260923-074848-afc4 (re-run; 074514-8243 was host-perturbed) | art:25be7fb3… | 0.0510 | 0.0192 | 0.0706 | 0.548 | 4.31e7 |
| bf16-hopper int-nonZK | lane 29dd5b8 | r20260923-082142-d70a | art:58f13190… | 0.0509 | 0.0194 | 0.0706 (1.87x) | 0.582 | 4.57e7 |
| bf16-hopper int-nonZK | lane 15d370e | r20260923-093927-06f2 | art:b2b4c784… | 0.0432 | 0.0190 | 0.0625 (2.12x) | 0.543 | 4.27e7 |
| fp8-hopper int-ZK | main 6babe27 | r20260923-074252-b61d | art:697819e8… | 0.0585 | 0.0250 | 0.0838 | 0.420 | 6.60e7 |
| fp8-hopper int-ZK | lane 247379e | r20260923-074227-4a84 | art:3a117853… | 0.0417 | 0.0111 | 0.0531 | 0.368 | 5.79e7 |
| fp8-hopper int-ZK | lane 29dd5b8 | r20260923-082025-839f | art:37993420… | 0.0332 | 0.0105 | 0.0439 (1.91x) | 0.349 | 5.49e7 |
| **fp8-hopper int-ZK** | **lane 15d370e** | **r20260923-093902-224b** | **art:aa3512ad…** | **0.0284** | **0.0105** | **0.0391 (2.14x)** | 0.369 | 5.80e7 |
| fp8-hopper int-nonZK | main 6babe27 | r20260923-074712-ecf3 | art:8a1506b3… | 0.0457 | 0.0243 | 0.0701 | 0.359 | 5.64e7 |
| fp8-hopper int-nonZK | lane 247379e | r20260923-074647-9f88 | art:a879fc7b… | 0.0271 | 0.0106 | 0.0377 | 0.331 | 5.21e7 |
| fp8-hopper int-nonZK | lane 29dd5b8 | r20260923-082115-3f71 | art:da8b63bc… | 0.0273 | 0.0109 | 0.0384 (1.83x) | 0.385 | 6.05e7 |
| fp8-hopper int-nonZK | lane 15d370e | r20260923-094013-2f1b | art:52f6a5db… | 0.0234 | 0.0106 | 0.0341 (2.06x) | 0.323 | 5.08e7 |

(`encode` = `split.encode_seconds`, `merkle` = `split.merkle_seconds`, sum = `t.encoding_commitment`; overhead against
989.4e12 / 1979e12 FLOP/s. Every row `validation: passed`, batch ACCEPT at 2^-128.05 (bf16) / 2^-128.32 (fp8), 25/25
resp. 13/13 dumps accepted cold by the Python file verifier; the pod's Rust `ligero-verify batch` on the validation
dumps ACCEPT (§3). Transcript bytes identical to main's, so the proofs are the same proofs.) **t.total is noisy on this
pod: ±5–10 % run to run on the host-bound phases** (tests / serialization / witness — hp2-host's), e.g. the two lane
non-ZK bf16 rows 0.548 vs 0.582 with identical encode/merkle splits, and r20260923-074514-8243 (reps 0.99 / 0.92 /
0.57, t.witness 0.126 vs 0.088) which I re-ran. Read the encode / merkle columns; they are stable to ±2 %.

Per bf16-hopper sub-batch (3328 rows x l=16384 -> 872 MB codeword), kernel microbenchmarks (H100, `microbench.py`,
`encode_simt_test`, median of 5–9):

| kernel | main 6babe27 | 429f8ea (cp1) | 29dd5b8 (cp2) | **15d370e (cp4, staged store)** | |
|---|---|---|---|---|---|
| encode, plain (int64 rows in) | 3.45 ms (253 GB/s of codeword) | 2.42 ms | 1.99 ms (439 GB/s) | **1.74 ms (500 GB/s)** | bit-exact |
| encode, ZK + coefficients | 3.52 ms | 2.48 ms | 2.12 ms | **1.86 ms** | bit-exact |
| encode, l=8192 / l=4096 (3328 rows) | 1.21 / 0.34 ms | | 0.97 / 0.26 ms | **0.78 / –** | bit-exact |
| Merkle commit (Blake3 leaves + 16 levels) | 1.89 ms (462 GB/s) | 0.70 ms | **0.73 ms (1.19 TB/s)** | same | same leaves/levels/root |
| the ZK "encode" lap's torch work around the kernel | ~1.7 ms (zeros 0.29 + int32→int64 0.26 + `eval_on_coset` on 36 mask rows 1.19: ~1200 launches) | same | **~0.3 ms** (two small zero fills, `_add_zh_times` 0.09, `encode_coefs` 0.16) | same | bit-exact |
| encode(ZK) + Merkle in the prover | 6.3 ms -> x25 = **0.158 s** | | 3.3 ms -> x25 = 0.0825 s (1.92x) | **2.9 ms -> x25 = 0.0724 s (2.19x)** | |

Target ≤ 0.05 s: not reached (0.0724 s; 2.19x of the 3x). The encoder is instruction-issue-bound at ~60 % of the H100's
SIMT issue roof, not DRAM-bound; the store pattern lever (0.45 ms) is now half taken (STAGE, −0.23 ms; the coset-major
layout is 0.19 ms further and needs the protocol's order to change — not taken). What is left is in §5.

## 1. Attribution (H100, main 6babe27; profile runs r20260923-055953-7662, r20260923-060111-3131)

Nsight Compute is not usable in the RunPod container (`ERR_NVGPUCTRPERM`, "No kernels were profiled", even with the
GPU idle) — attribution is by ablation (variant kernels timed with cupy events), static SASS (`cuobjdump -sass`, opcode
histogram, ptxas register/spill report, `sass.py`) and occupancy arithmetic.

Encoder `rs_encode_ligero` (main): one 1024-thread CTA per row, 5 NTTs of size 16384 per row (INTT + 4 twisted coset
NTTs), radix-4 shared-memory stages + 4 radix-2 register stages; 64 KiB dynamic smem; ptxas: 64 registers, **64 B
spill**, 4096 SASS instrs (IMAD 1334, ISETP 693, IADD3 630, LDS/STS 175 each, LDG 102). Occupancy: 1 CTA/SM by
registers (64 x 1024 = the file), 32 warps/SM. Passes over the row per sub-batch: message read once (218 MB), codeword
written once (872 MB) — then re-read by the hasher (872 MB), by the prover's tests (`quad_p0`, `U[mr[..]]`,
`index_select`, int64 — several passes, hp2-host's phase) and by the openings (`U32.index_select(1, cols)`, 197
columns). Effective 253 GB/s vs 3.35 TB/s HBM3: the kernel is not DRAM-bound.

Ablations on the checkpoint kernel (l=16384, 3328 rows; "(!)" = wrong output, timing only), run r20260923-061443-5caa +
`enc_v3.py`/`enc_conf.py` (07:00Z):

| variant | ms | says |
|---|---|---|
| checkpoint kernel | 2.42–2.61 | |
| (!) no codeword store at all | 1.54–1.56 | the skeleton (loads, 5 NTTs, barriers) is 60% |
| (!) coset-major coalesced store | 1.84 | a 4-B store at stride 16 B costs 16 L2 sectors per warp instruction; **0.58 ms** |
| paired 8-B stores via smem (`y`) | 2.42 (= 4-B) | same sector count, no gain -> dropped again |
| (!) low-m DIT passes lane-consecutive (no bank conflicts) | 2.06 | the m=1,4,16 radix-4 passes are 2–4-way conflicted: **0.55 ms** |
| (!) no smem-stage butterflies (loads/stores kept) | 2.29 | arithmetic in the smem stages is ~3% |
| (!) mont_mul -> xor everywhere | 2.57 | the Montgomery arithmetic is not the limit |
| (!) constant twiddles (register stages) | 2.22 | twiddle LDGs miss L1 (192 KiB smem carve-out leaves ~40 KiB L1) 0.14 |
| coefficients in L2 instead of smem | 2.80 | |
| 512 threads x 2 CTAs/SM | 2.37 (= 1024 x 1) | occupancy alone is not the lever |

Attribution AFTER (kernel v3 = 29dd5b8, l=16384, 3328 rows, `enc_v3_tune.py` / `enc_v3_l2.py` / `sass2.py`, 07:00–07:20Z):

| variant | ms | says |
|---|---|---|
| v3 (final: evict_last store, launch_bounds) | 1.94–2.06 | 439 GB/s of codeword |
| (!) no codeword store | 1.38 | the compute skeleton (5 transforms, 9 barriers, twiddle loads) |
| (!) coset-major coalesced store | 1.49–1.50 | the natural-order store costs **0.45 ms** (was 0.58; evict_last took 0.1) |
| plain 4-B stores vs `st.global.L2::cache_hint` evict_last | 2.045 vs 1.942 | the partially written 32-B sectors (8 B per coset) otherwise get written back up to 4x |
| `__stcs` / `__stwt` stores | 2.046 / 2.054 | no |
| grid 528 / 132 / 66 / 33 blocks | SM-µs per row 81 / 84 / 73 / 72 (coset-major: 60 / 58 / 56) | 3/4 of the store penalty is intrinsic to the pattern, 1/4 is DRAM/L2 contention |
| `#pragma unroll 1` on the pass groups | 2.06 vs 2.49 (full unroll spilled 200+ B) | register pressure at the 64-register cap decides |
| launch_bounds(T,2) at l=8192 | 1.157 -> 0.985 (regs 128/208 B spill -> 64/16 B) | two 512-thread CTAs per SM |
| `__ldg` vs volatile-asm twiddle loads, blocks 1x/2x/8x SMs | ±1 % | not levers |

Static SASS (sm_90, `sass2.py`): 2896 instructions, **0 B spill**, 64 registers; `VIADDMNMX.U32` x601 — Hopper fuses
the min-trick reductions (`min(s, s-P)`) into one instruction, so a butterfly is 9 instructions (IMAD.WIDE, IMAD,
IMAD.HI, IADD3, VIADDMNMX for the Montgomery product; IADD3 + VIADDMNMX twice for the sum/difference). Dynamic estimate:
5 transforms x 112 butterflies x 9 + smem / twiddle / address ≈ 7 k instructions per thread per row -> 0.75 G
warp-instructions per sub-batch -> **0.80 ms at the H100's issue rate** (132 SMs x 4 schedulers x 1.755 GHz); the
skeleton measures 1.38 ms (58 % of the issue roof: barriers with one CTA per SM, LDG twiddle latency). So the encoder
is **instruction-issue-bound**, not memory-bound: 439 GB/s is 13 % of HBM3 but the butterfly count is the wall.
BabyBear at 31 bits leaves no headroom for lazy reduction in u32 (2p < 2^32 < 3p), so the 9-instruction butterfly is
close to minimal for a SIMT NTT; the remaining levers are the store pattern (0.45 ms) and barrier/latency hiding.

Store AFTER (15d370e `STAGE`, `enc_stage_abl*.py`, 09:15–09:30Z; l=16384, 3328 rows, same run for every row):

| variant | ms | says |
|---|---|---|
| unstaged (4-B stores at stride 16, evict_last) | 1.99–2.00 | the cp2 kernel |
| (!) coset-major store (wrong order) | 1.58 | the floor of the store pattern |
| **staged, read-back `#pragma unroll 4`** | **1.77** | −0.23 ms; 0 B local |
| staged, read-back fully unrolled | 1.94 | 104 B spilled at the 64-register cap — the first version |
| staged, read-back unroll 2 / 8 | 1.78 / 1.78 | |
| (!) staged, no read-back / no staging stores | 1.84 / 1.92 (spilled builds) | the L2 round trip itself is ~0.1 ms |
| staged, plain uint4 final store (no evict_first) | 1.79 | the policy is worth 0.02 |
| unstaged, grid 132 (= resident CTAs) instead of 528 | 2.09 vs 2.00 | the STAGE grid costs ~0.05 of tail, already inside the 1.77 |

Per row: 3 x 64 KiB staged out and back through L2 (25 MB resident for 132 CTAs, evict_last), 256 KiB of codeword in
16-B stores with evict_first. The remaining 0.19 ms to the coset-major floor is the L2 round trip plus the 132-CTA
tail; a 4-CTA cluster with DSMEM exchange (§5.1) would remove the round trip but not the tail.

Skeleton decomposition of the 15d370e kernel (`enc_skel.py`, 09:57Z, l=16384, 3328 rows, one run; (!) = wrong output,
timing only; baseline 1.80 in this run):

| variant | ms | says |
|---|---|---|
| (!) no `__syncthreads` at all | 1.44 | **the ~20 barriers per row cost 0.37 ms** (one 1024-thread CTA per SM drains at each) |
| (!) no strided smem passes (10 of the 15 passes) | 1.27 | the strided passes (loads, stores, butterflies) are 0.53 |
| (!) no strided DIT passes (8 of 15) | 1.36 | |
| (!) register stages -> identity (loads/stores kept) | 1.52 | the 20 register stages' butterflies are 0.28 |
| (!) 1 coset NTT instead of 4 | 0.85 | a coset transform + its store ≈ 0.32 |
| (!) all twiddle loads -> constants | 1.59 | **0.22 ms in twiddle loads + index arithmetic** |
| twiddles of the smem passes in shared memory (bit-exact, tried in a branch) | 1.75 vs 1.74 | **no gain**: the cost is the index arithmetic and issue slots, not L1 misses -> reverted |
| (!) all butterflies -> xor (loads/stores/barriers kept) | 1.12 | field arithmetic ≈ 0.68 of 1.80 |
| (!) mont_mul -> xor (adds kept) | 1.25 | the Montgomery products ≈ 0.55 |

So: arithmetic 0.68, barriers 0.37, twiddle indexing 0.22, store 0.19 (+ the DRAM write), the rest is smem traffic and
loads. The arithmetic is at its 9-instruction-per-butterfly floor; the barriers are the structural cost of one CTA
per SM (see §5.2).

Merkle AFTER (`commit_gpu`): 0.73 ms = leaves ~0.67 + tree 0.05; `blake3_leaves` 1784 SASS instructions (two inlined
compressions of ~720 each: LOP3 466, SHF 455, IADD3/IMAD.IADD 470), 46 registers, no spills; 14.4 M compressions x 720
= 10.4 G thread-instructions -> **0.35 ms at the issue roof**; measured ~0.67 -> ~55 %. Ablation (`mk_abl.py`, run
09:12Z, 3328 x 65536, same run): leaves 0.648 ms (1.35 TB/s of codeword read); **compute only (no loads) 0.545**;
**loads only (no compression) 0.469** (1.86 TB/s: the 128-B-per-row-per-warp pattern is at ~55 % of HBM3); loads only
with 512-B row segments (uint4 per lane over a 128-column tile) 0.390; `launch_bounds(416,4)` 0.724 (32 regs, worse),
(416,3) 0.656, (416,2) 0.679, (512,3) 0.666, PREFETCH=1 0.674, rotr 16/8 via PRMT 0.648 (= baseline). So the leaves
kernel is compute-bound with imperfect overlap (0.648 = 0.545 + 0.10): the Blake3 compression instruction count is the
wall, the 128-column tile would take ≤ 0.08 ms off the load side, and no launch-bounds / prefetch / rotate variant helps.
**Two columns per thread (two interleaved Blake3 chains for ILP, `mk_ilp.py`, 10:30Z, bit-exact): 0.630 ms at 64
registers (32 B spill, 2 CTAs/SM) vs 0.648; 0.760 at 93 registers (1 CTA/SM).** −3 %: the 26 warps per SM already
cover the G-function's dependency chain; the compression is ALU-issue-bound at ~720 instructions. Not adopted.

Merkle (main): `backends/shared/hash_gpu` Blake3, per level a launch (~20 launches), `blake3_chunks` 42 regs with a
`__constant__` message-permutation table -> the 16-word block lives in local memory (96 LDL + 24 STL per compression);
1.888 ms for 872 MB (462 GB/s).

## 2. What changed (all under `backends/direct/ligero/`)

`encode_simt.py` — kernel v3 (bit-exact with main's kernel at l ∈ {256, 4096, 8192, 16384}, plain / ZK mask fold-in /
coefficient output / coefficient-form rows; `encode_simt_test` PASS on the pod): every thread owns 16 elements in every
phase, `THREADS = l/16`; a transform = 4 radix-16 register stages (elements t + THREADS·s) + three shared-memory passes
of 4 stages each (stride 256, stride 16, 16 contiguous) — 3 smem round trips instead of 5 and no separate scale/copy
passes (the last INTT pass writes the bit-reversed unscaled coefficients `cf`, each coset's first pass reads, scales by
`l^-1 (g w_n^c)^i` and folds the mask in); XOR bank swizzle `SWZ` makes all pass patterns and the bit-reversed
coefficient gather conflict-free, 16-byte vector smem accesses in the contiguous pass; branch-free min-trick
reductions; `__launch_bounds__(THREADS, THREADS <= 512 ? 2 : 1)`; the natural-order codeword store carries an L2
`evict_last` policy (`createpolicy` + `st.global.L2::cache_hint`, sm_80+; plain store otherwise) when `stage=False`.
New in 15d370e (`STAGE`, sm_80+ default): the coset-3 pass writes each position's four cosets as one 16-byte
`evict_first` store after reading cosets 0–2 back from a per-CTA staging buffer (`stg`, `blocks x 3 l` words) that the
earlier passes filled coset-major with `evict_last` stores — the same thread writes and reads the same addresses, so no
barrier or fence is needed; the grid is exactly the resident CTAs (1 x SMs at 1024 threads, 2 x SMs at ≤ 512) so the
buffer (25 MB at l=16384 on the H100) stays in the 50 MB L2. `CF_GLOBAL` (af3b7de): cf in a per-CTA L2 scratch when
`2 l x 4 B > sharedMemPerBlockOptin` (Ada / consumer Blackwell at l=16384; +10 % on the H100 when forced). New in 29dd5b8:
int64 rows are read in place (no int32 copy: 0.22 ms), `encode(..., coefs_out=)` writes the int64 coefficients into
any row-contiguous view (the prover's `coefs[:m, :l]`), and **`encode_coefs(coefs (R, l+t_pad) int64, out=)`**
evaluates coefficient-form rows (the ZK mask rows, degree < k) with the same kernel compiled with `COEF_IN=1`: no
INTT — `cf[brev(j)] = l·c_j` — and the high part `c_hi` enters exactly like the witness mask with the per-coset
constant `x^l = z_c + 1` instead of `z_c` (`mask1` table). Bit-exact with `eval_on_coset` (exact field arithmetic).

`commit_gpu.py` (new; `merkle.commit_device` uses it when n is a power of two and rows ≤ 4096, `USE_FUSED_COMMIT`
flag, `hash_gpu` stays the reference and fallback): leaf = Blake3(column bytes, 13 chunks of 1 KiB), node =
Blake3(l || r) with the spec's chunk tree — the bytes `merkle.verify_path` and the `blake3` package hash. Kernel
`blake3_leaves`: one block per 32 columns, one warp per chunk (a warp's load = 128 contiguous bytes of one row), the
13 chaining values meet in smem `[chunk][word][lane]` (conflict-free) and the block finishes the chunk tree; the
7-round message schedule is a `constexpr` table (no local memory). `blake3_tree`: 9 levels per launch in smem (every
level written — the openings need siblings), one more launch for the top. 3 launches, no host syncs, cupy views per
level (`Tree.levels`), `open_device` unchanged. 0.70–0.78 ms vs 1.89 (leaves 0.67, tree 0.05).

`protocol.py` (hp2-host's file; diff confined to the ZK encode block, lines 871–889): `coefs = torch.empty` + `coefs[:m, l:] = 0`,
`coefs[m:] = 0`, `enc.encode(W, S["W"], out=U[:m], coefs_out=coefs[:m, :l])`, and `enc.encode_coefs(coefs[m:], out=U[m:])` for
the mask rows (guarded by `Mrows > m`); the torch fallback branch is unchanged. Everything downstream (`_add_zh_times`, the
tests, openings) sees the same tensors with the same values. `commit_gpu_test.py`:
every level/leaf/root vs `hash_gpu` + `blake3` at the four provers' shapes and edge cases (partial chunks, N=2,
odd chunk counts), openings verify, negative path, stream argument. (Found and fixed before the commit: a
`__syncthreads()` inside a lane-divergent branch hung the kernel for N < 32 columns.)

Interface for hp2-host: `encode_simt.LigeroEncoderSIMT.encode(rows int32|int64, mask=None, want_coefs=False, out=None,
stream: torch.cuda.Stream | None = None, coefs_out=None)`, `.encode_coefs(coefs, out=None, stream=None)` and `merkle.commit_device(U_int32, stream=None)` /
`commit_gpu.commit(U, stream=None)` launch on the given torch stream (default: torch's current stream).

## 3. Evidence (runs r20260923-064515-edd8 [429f8ea], r20260923-073018-cb94 [247379e], r20260923-080923-40cf [29dd5b8], r20260923-085822-cb9f [af3b7de], **r20260923-092554-cc4c [15d370e]**; lane tree vs /workspace/src-main = main 6babe27)

Bit-exactness harnesses: hostphase's `bitexact.py` (relchain runner in-process, `os.urandom` = seeded SHAKE-256 so
the interactive coins AND the ZK mask keys replay) for bf16-hopper (3 x 170 VUs) and fp8-hopper (3 x 341); new
`bitexact_cli.py` (same seeding around `run.py main(argv)` + `--dump-dir`) for the vu.py Ampere relation (bench-vu
--batch 16384 --total-vus 340) and fp4-nvf4 (--batch 4096 --total-vus 170). sha256 of every system.bin / .stmt /
.proof / .coins: **60/62 identical in the run**; the 2 differing files (fp4-nvf4 int-ZK sub_00.coins + .proof, stmt
and system identical) were a harness artifact: the *main* tree's first fp4-ZK process compiled its l=4096 kernel,
cupy writes the kernel cache through `tempfile`, whose name generator seeds Python's `random` from `os.urandom` —
one extra draw from the seeded stream shifted main's coins. Re-run with warm caches (both trees, either order):
fp4-int-zk **4/4 identical** (`bitexact/fp4zk_rerun.txt`; main's warm-cache hashes equal the lane's cold-run ones).
Fixed in `validate2.sh`: a throwaway-seed warm-up of every relation/mode in both trees before the seeded pairs -> the
cp2 runs give **62/62 identical** (both r20260923-073018-cb94 and r20260923-080923-40cf).

Rust: `diff -rq backends/ligero-verify` main vs lane empty; `ligero-verify batch --target-bits 128` on every lane dump
tree (all three validation runs): bf16-hopper ZK/nonZK 3/3 accepted (2^-128.41 / 2^-128.60), fp8-hopper 3/3 (same),
bf16-ampere 2/2 (python_agree 2/2), fp4-nvf4 1/1 (python_agree 1/1). pytest 68 passed / 1 skipped / 2 deselected
(206–221 s). The 13 benchmark rows: `validation: passed` (live verifier every rep + Python file verifier cold on every
dumped proof, batch ACCEPT); Rust on their dump trees is the coordinator's step (dumps in the run_files artifacts). Gates: bf16-ampere rc=0
(52 negatives, 252 mutations rejected), bf16-hopper rc=0 (87 negatives), bf16-hopper --zk rc=0, fp8-hopper rc=0 (92),
fp8-ada rc=0 (92), fp4-nvf4 rc=0 (114 + 3015 unit negatives).

## 4. Runs (campaign r21-enc-hopper, vy-enc-hopper)

| run | what |
|---|---|
| r20260923-055500-137d | bootstrap (venv312 torch 2.6.0+cu124, cupy 14.2, blake3, rustc 1.98.1, ligero-verify, bench-instances, src-main) |
| r20260923-055953-7662 | main microbench + ncu attempt (ERR_NVGPUCTRPERM) |
| r20260923-060111-3131 | SASS / ptxas static analysis of main's kernels |
| r20260923-060806-518a … 061443-5caa | commit_gpu dev, encoder ablations (v2 smem coefficients) |
| r20260923-062104-79f1 | v2 encoder + fused commit tests + microbench |
| r20260923-064515-edd8 | **checkpoint-1 validation** (pytest, bit-exact x8 pairs, Rust, 6 gates) |
| r20260923-073018-cb94 | validation of 247379e (kernel v3) — 62/62, pytest 68, Rust, 6 gates |
| r20260923-074052-bb4f … 074712-ecf3, 074848-afc4 | 9 benchmark rows: lane 247379e and main 6babe27, bf16-hopper + fp8-hopper, int-ZK + int-nonZK (074514-8243 perturbed, re-run 074848-afc4) |
| r20260923-080740-9e3d, 082025-839f, 082115-3f71, 082142-d70a | **lane 29dd5b8 benchmark rows** (bf16h ZK / fp8h ZK / fp8h nonZK / bf16h nonZK) |
| r20260923-080923-40cf | **checkpoint-2 validation** of 29dd5b8 — 62/62 identical, pytest 68, Rust ACCEPT x8, 6 gates |
| r20260923-085822-cb9f | checkpoint-3 validation of af3b7de (CF_GLOBAL) — 62/62, pytest 68, Rust x8, 6 gates |
| r20260923-092554-cc4c | **checkpoint-4 validation** of 15d370e (STAGE) — 62/62, pytest 68, Rust ACCEPT x8, 6 gates, encode_simt_test PASS (both store paths) |
| r20260923-093805-28f2, 093902-224b, 093927-06f2, 094013-2f1b | **lane 15d370e benchmark rows** (bf16h ZK / fp8h ZK / bf16h nonZK / fp8h nonZK) |
| r20260923-093610-07e9, 093635-dbd1, 093659-50b1, 093724-6594 | 4 failed launches (rc 2 in 21 s: a zsh word-splitting slip passed a bad `--relation`); no result, ignore |
| r20260923-101926-dcdc | **checkpoint-5 validation** of 0da4b1b (n/l ∈ {2,4,8}) — 62/62, pytest rc=0, Rust ACCEPT x8, 6 gates, encode_simt_test PASS incl. n = 2 l / 8 l |
| r20260923-104941-5d2f, (fp8h follows) | lane 0da4b1b bf16h / fp8h int-ZK confirmation rows (pod migrated to a new host at ~10:00Z: same Xeon 8470 model, load avg 8 — not like-for-like with the 07–09Z rows) |

All runs pulled (`research data pull`, `evidence/pull.log`), `research data push --pending` clean (89/89, 45/45,
49/49, 15/15), snapshots `enc-hopper-v2` = art:17feca22e1f21f5e9b813b2d7d962e425425b2b9840f7c70dfa377299c841ddd and
**`enc-hopper-v3` = art:ee9b62fd80eb445b789e1a213480bcd7abb4d852c64e9e51045b863da51f9613**; every bench result
labelled `note=` (pod / host / load / splits), `tree=`, `row=` `--by enc-hopper --ref <run>`. No `verified=` labels.
**Pod terminated 11:55Z** (`research pods terminate de87jjrsjm8pdg`, gone from `pods list` at 11:56Z): 05:47Z -> 11:55Z =
**6.1 pod-hours ≈ $21.5** (budget 7.5 h / $26). Every pod run pulled (`data pull`, incl. the early profile / dev / cp1 runs
055953-7662, 060111-3131, 060806-518a, 061020-f214, 061244-1a14, 061443-5caa, 062104-79f1, 064515-edd8, 055500-137d pulled at
11:45Z); `data push --pending` was still uploading the two cp5 run_files dump trees at 11:55Z while another lane's push held
the shared store (their results, events and snapshot v5 are PRESERVED). Final snapshot **enc-hopper-v5 =
art:70dc6cae88567987dad9a30b3f1ba826f9d75dbc08cc0cadee2d9f04f5c1d7fe** (v4 + the two 0da4b1b rows + events).
Pod-hours at 09:50Z: 4.05 h ≈ $14; at 10:55Z 5.1 h ≈ $18 (pod migrated by RunPod to a new host ~10:00Z, /workspace intact,
`machines.toml` keyed by pod_id so `research run` followed it). Shared-store note: `data push --pending` reports
art:b634b6c0… (run-files of **another lane's** run r20260923-093845-4767, live-verifier sessions) with 114 blobs missing
locally and remotely — not created or evicted by this lane (`store_evict.py` only drops blobs whose every holder is
verified remote); that lane should re-pull it from its pod.

## 5. Next (ranked, with the measured upper bounds; per bf16-hopper sub-batch, x25 for the run)

Where the 2.9 ms (encode ZK 1.86 + torch 0.3 + Merkle 0.73 + laps) go and what each lever is worth:

1. **The codeword store: 0.19 ms left (bit-exact).** STAGE took 0.23 of the 0.45 (1.99 -> 1.77; the coset-major layout
   is the 1.58 floor). What remains is the L2 round trip of cosets 0–2 and the resident-grid tail. Options: (a) a
   **4-CTA cluster per row** on sm_90, one coset per CTA, the INTT register stages split over the cluster's 4096 threads,
   the 1024-blocks exchanged through DSMEM, `cf` broadcast, a final 4-way DSMEM interleave with 16-B stores — removes
   the round trip (≤ 0.1 ms) and also parallelises the row 4-way (the barrier count per row drops), 2–3 hours under
   NVRTC (`__cluster_dims__`, `cooperative_groups::cluster_group`, `mapa`), untested; (b) at l ≤ 8192 the four coset
   outputs fit shared memory next to `cf` (4 x 32 + 32 KiB) — no L2 trip, 1 CTA/SM instead of 2, ~1 hour; the fp4 shape
   (5090, l=4096) and fp8/bf16 at l=8192 would take it.
2. **Barriers, 0.37 ms (measured by removing them, §1), and twiddle indexing, 0.22 ms.** One 1024-thread CTA per SM
   drains at each of ~20 barriers per row. Two CTAs per SM at l=16384 are impossible (registers: 64 x 1024 x 2 = 2 x
   the file; smem: 2 x 128 KiB > 227). What would work: (a) **THREADS = l/32 (512 threads, 32 elements per thread,
   radix-32 register stages, 2 CTAs/SM by smem with `CF_GLOBAL`-style cf in L2 or 3 passes of radix-8 for the
   remaining 9 stages)** — the registers (32 elements + twiddles + addresses at a 64 cap) are the risk, expected ≤ 0.3
   ms if it fits; (b) the 4-CTA cluster (item 1a) which also cuts the barrier count per row 4-way. The twiddle
   indexing: `m + (idx & (m-1))` per butterfly is an IADD3/LOP3 + the load; moving the loads to shared memory did
   nothing (1.75 vs 1.74, tried, reverted), so the lever is fewer twiddle *loads* — radix-4 butterflies share
   twiddles (w, w^2, w^3 from two loads instead of four) at +1 multiply: ≤ 0.1 ms, untested.
3. **Merkle leaves 0.65 ms vs 0.35 at the issue roof — measured (§1): compute-only 0.545, loads-only 0.469, sum >
   total, so both sides are ~85 % busy and overlap imperfectly.** The instruction count of the compression is the wall:
   the only real lever is fewer instructions per compression — (a) interleave two independent compressions per thread
   (ILP: the G-function's 4 dependent adds/xors/rotates per column stall the single chain; 2 chains ≈ +32 registers,
   from 59 -> ~90, 2 CTAs of 416 per SM instead of 3; expected 0.545 -> ~0.45), (b) the 128-column tile for the load
   side (0.469 -> 0.39 measured for loads-only; ≤ 0.08 ms on the total). No launch-bounds / prefetch / PRMT variant
   moved it (all within ±0.03 or worse). Ceiling for the whole Merkle: ~0.55 ms (−0.18 ms per sub-batch, −4.5 ms per run).
4. **The rest of the ZK encode lap (~0.3 ms)**: `_add_zh_times` (0.09, int64 slices), two zero fills, `encode_coefs`
   for the 36 mask rows. **Tried and dropped (10:00–10:25Z, all bit-exact):** (a) the mask rows as extra rows of the
   main launch with a per-row runtime "coefficient input" branch — 136–192 B of spills at the 64-register cap, plain
   1.74 -> 1.81, ZK 1.86 -> 2.20 ms; (b) the same with the coefficient path `__noinline__` — 640 B of spills, worse;
   (c) the mask-row launch on an internal side stream forked before the main launch so it runs in the main launch's
   tail — measured: the serial cost of the 36-row launch behind the main one is only **0.048 ms** (not the 0.16 of a
   standalone launch), the side stream saves 0.035 of it. Not worth a stream inside `encode()` for 1 ms per run; kept
   in `evidence/scripts/encode_simt_sidestream.py` if hp2-host's pipelining wants the fork/join pattern.
5. **Encode-and-hash fusion** (brief item 3): the hasher is at 55 % of the issue roof and not DRAM-bound, the encoder is
   issue-bound too — fusing them saves at most the 872 MB re-read (0.26 ms of DRAM time that is already overlapped with
   compute). Below items 1–3; the tile version (a 256-row band encoded then hashed from L2) needs 64 MiB bands ≥ the
   50 MiB L2 — 128-row bands with a 2-level chunk tree change nothing in the protocol but need a band-ordered launch.
6. **Protocol-changing (not taken; expected gains are small for the prover clock):** (a) tree arity 4/8: `blake3_tree`
   is 0.05 ms and 16 levels x 32 B x 197 paths = 101 KB per proof -> 50 / 38 KB; verifier path checks 16 -> 8 / 6
   hashes but 3 / 7 siblings each; a proof-format change through `serialize.py` + Rust for ≤ 0.05 ms and −50 KB —
   not worth the freeze risk tonight. (b) Wider leaves (2 columns per leaf): halves the leaf count, not the hashed bytes
   (compression-bound), −16 KB of paths per proof; the openings would send 2 columns per query -> +197 x 13 KB of
   proof. No. (c) Lower rate: **done in 0da4b1b** — the kernel takes `NC = n/l ∈ {2, 4, 8}` cosets (tables NC×K,
   NC×TP; the staged store parks NC−1 cosets and writes 8 / 16 / 32 contiguous bytes per position). H100, 3328 rows,
   l=16384: n = 2 l **0.97 ms** (451 GB/s; unstaged 0.98), n = 4 l 1.73 (504 GB/s), n = 8 l **3.56 ms** (490 GB/s; the
   unstaged 4-byte-at-stride-32 store is 8.0 ms — the staging matters most at the low rate). ZK 1.03 / 1.84 / 3.68.
   `protocol._simt_encoder` accepts those rates (main: torch NTT, 25.5 / 81.4 ms). The n = 8 l staging buffer is 58 MB
   on the H100 (> 50 MB L2): part of the round trip spills to HBM but the stores stay full-sector. The rate sweeps at
   the freeze therefore see the fast encoder at every rate if the coordinator merges 0da4b1b.
7. **A100 / 4090 / 5090**: not measured tonight (one pod). The kernel is plain CUDA C (sm_80+ for the `createpolicy`
   hint, guarded by `__CUDA_ARCH__ >= 800`), 64 registers x 1024 threads = the A100/4090 register file too, 128 KiB
   dynamic smem (A100: 164 KiB/SM ok; 4090/5090: 100 KiB/SM — **l=16384 needs 128 KiB and will not launch on
   Ada/Blackwell consumer parts**: `max_dynamic_shared_size_bytes` > 99 KiB fails). fp4-nvf4 runs at l=4096 (32 KiB)
   and passed its gate on the H100; **lane fp4-fast moving fp4 to l=16384 on the 5090 would have hit this** — fixed
   in af3b7de: `CF_GLOBAL` puts `cf` in a per-CTA L2 scratch when `2 l x 4 B > sharedMemPerBlockOptin` (chosen at
   construction from the device properties; forced and tested bit-exact on the H100 at every l, +10 % there when
   forced: 1.94 vs 1.74 ms). Untested on an actual Ada/Blackwell part tonight (one pod): **the coordinator should run
   `python -m backends.direct.ligero.encode_simt_test` on the 5090/4090 before trusting the fp4 l=16384 numbers**; the
   STAGE buffer (25 MB at l=16384 for 128 SMs x 1) also assumes an L2 ≥ ~32 MB (4090: 72 MB, 5090: 96 MB, A100: 40 MB
   — the A100 at 108 SMs stages 21 MB, tight but inside; `stage=False` is the fallback if the A100 regresses).

## 6. Wrong / surprising in the spec

- Nsight Compute cannot run in these pods (no `CAP_SYS_ADMIN` / perf-counter permission); attribution had to be by
  ablation + SASS. The spec's "≥1 TB/s effective" is against a kernel that is not DRAM-bound at all — the row-per-CTA
  NTT is bounded by shared-memory passes/conflicts, barriers and the store pattern; 1 TB/s of codeword = 0.87 ms.
- `research pods create` from a backgrounded shell exited before writing `machines.toml` (registered by hand, as the
  spec anticipated). The local disk: Cursor's `state.vscdb` (58 -> 62 GB overnight) pushed free space under 2 GB and
  broke `research run` launches (`OSError: No space left on device` on the *laptop*); `store_evict.py` found nothing
  to evict — cleared `uv`/cargo/Sparkle caches. Worth a line in the campaign rules: check laptop `df` too.
- The seeded-`os.urandom` harness is fragile against *anything* that draws entropy: cupy's kernel-cache write does
  (via `tempfile`); the first process to compile a kernel shifts the stream. Warm the caches or pre-seed `tempfile`.
- hp2-host's tests re-read the codeword several times in int64; that phase, not encode/Merkle, is where the 872 MB
  "passes over the matrix" multiply.
