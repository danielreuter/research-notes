---
lane: jolt-scout
kind: report
created: 2026-09-25T06:47Z
status: final
---

CHECKPOINT 95facf3 (08:08Z) [final] NO-GO for Table 2: curve Jolt ~100-bit (BN254) + 125-bit challenges; ICICLE dead, lattice no CUDA, Jolt Pro closed. PR1618 CUDA works on 4090 (5.7-8x CPU at 2^24). VU committed keyed-BLAKE3 126.1k cyc/VU; 4096 VUs ~5-14 min/4090. Pod terminated 08:07Z, ~$1.00. art:a53998e6
CHECKPOINT a33671b (08:04Z) [open] 08:04Z: adopted survey rec: keyed-BLAKE3 row leaves via compression inline = 81.5k cyc/VU (SHA-256 195k); committed 126.1k/VU, digests match blake3 crate, B=64 CPU 30.5s valid. hash-bench: SHA-256 ~1,915/compression, BLAKE3 ~700. Running BLAKE3 guest on PR1618 cuda.
CHECKPOINT 597b6c6 (07:56Z) [open] 07:55Z: VU guest on PR1618 cuda (4090): committed B=48 2^24 9.50s (CPU 54.5s), B=64 2^25 20.6s/22GB; bare B=256 2^24 16.8s (CPU 50.0s, only 3.0x). Projection 4096 committed ~11 min/4090 in ~70 2^24 proofs. Running hash-bench for BLAKE3 vs SHA-256 inline cost.
CHECKPOINT d69d082 (07:39Z) [open] 07:41Z: PR1618 CUDA on 4090 works: sha2-chain 2^24 prove 5.83s vs CPU 46.5s (8.0x; 2^22 5.8x), GPU mem 12.7GB@2^24. VU guest v2: 43.8k cyc/VU bare, 239.5k committed; B=64 committed CPU 55-62s. BlindFold ZK +3-5%. Next: VU guest on PR1618 cuda.
CHECKPOINT 9bfc8e2 (07:31Z) [open] 07:31Z: 4090 pod up. VU guest: kernel 34.1k cyc/VU, SHA-256 rowhash 195k/VU; B=16 committed CPU prove 26.4s valid. ICICLE path dead (removed #822, last rev broken). PR1618 CUDA built sm_89/nvcc12.9, sweep queued. ZK build running. Lattice/LayerZero: no CUDA/closed.
CHECKPOINT 00ffe398 (07:08Z) [open] Dory+ICICLE never coexisted (Dory hard-codes use_icicle=false @16763aac); PR#1618 = curve/Dory CUDA draft, not lattice; Akita lattice: no CUDA, no zk; Jolt Pro closed. Building main VU guest (bare kernel verbatim) + old ICICLE rev on 4090
CHECKPOINT 7fcedf47 (06:47Z) [open] startup: jolt main has no ICICLE (removed #779 2025-07-15/#822 2025-08-01; README 'pre-alpha, do not use' since #730); Akita lattice PCS merged 09-15, PR#1618 still draft; pod vy-jolt-scout 4090 up; next: build icicle rev 4c259be4 + main on pod

# jolt-scout: can Jolt (a16z) be a Table 2 backend? (feasibility scout)

Status: measurements done 08:05Z, pod terminated 08:07Z; FINAL section at the end. Evidence (every pod log, bench
output, GPU sample, script and the guest source): art:a53998e6d3c89ac1e579bc974c417f0928f33aad8adea1fa0fa66148c80dbb52. Pod vy-jolt-scout (RTX 4090 24 GB, Ryzen 9 7950X
16 vCPU, driver 580.159.04, CUDA 12.4 image + CUDA 12.9 nvcc installed). Scripts: `evidence/pod-scripts/` (00-setup, 10/11/12
main, 20-22 ICICLE, 30 PR #1618, vu-k1536/ = the VU guest).

## Source findings (GitHub, 2026-09-25)
- a16z/jolt main @ 922af71c (2026-09-24): RV64IMAC; modular prover (`crates/jolt-prover`, `--backend reference|optimized`);
  PCS Dory over BN254 (default) or Akita (lattice, `akita` feature, from LayerZero-Labs/akita, merged 2026-09-15 #1675/#1676/#1718).
  ZK: BlindFold (eprint 2025/2094, PR #1205 merged 2026-09-15), `zk` feature, Dory only; `akita`+`zk` is a compile error.
  Transcript default LegacyBlake2b (Keccak optional; Poseidon optional). No `icicle` feature anywhere on main.
- ICICLE history: added #503 (2025-01-07) for jolt-core MSMs (HyperKZG/Zeromorph era); README "CUDA acceleration is still a
  pre-alpha WIP and should not be used" since #730 (2025-06-27); dispatch code deleted in #779 (2025-07-15); Cargo feature deleted
  #822 (2025-08-01). The SDK switched to Dory only at fd3ffb6a (2025-07-30, tag v0.2.0-alpha), after the dispatch was gone. The one
  side-branch commit carrying both (16763aac, 2025-07-28) calls `msm_field_elements(..., use_icicle=false)` in every Dory MSM.
  => "curve Jolt (Dory/BN254) + ICICLE" never existed; ICICLE only ever accelerated >64-bit-scalar G1 MSMs of HyperKZG.
- PR #1618 "Draft: CUDA kernels" (protoben; head 66e33a9e 2026-09-02; base main 2026-08-17; +74.8k lines): a native CUDA
  backend for the modular prover, CURVE Jolt (jolt-kernels/jolt-dory/jolt-crypto; 44 .cu kernels incl. MSM, pairing,
  booleanity, RAF, opening). Not lattice. Author: "3.5x speedup with 1 GPU, 4.9x with 2 GPUs on a 2^24 trace". Draft, unreviewed.
- Lattice Jolt (Akita): no CUDA code (akita specs only say "downstream Metal/CUDA backends remain free to ..."), no GPU branch,
  no ZK. Per user decision: skipped (no CPU runs). PR #1733 "Metal GPU backend (experimental)" is Apple-only.
- LayerZero "Jolt Pro" (Zero chain): NOT open source (no repo under LayerZero-Labs; positioning paper describes it as their
  prover). Claims: 64x RTX 5090 cell proves 1.61e9 RISC-V cycles/s (~25M cycles/s/GPU), "succinct proofs, ZK on the roadmap".
  LayerZero's open pieces are akita (lattice PCS) and ZeroOS (std guest target riscv64imac-zero-linux-musl, used by Jolt).

## Security (curve Jolt, Dory/BN254)
- Computational: Dory binding reduces to SXDH/DL in BN254 (G1, G2, GT via pairing). GT DLP by SexTNFS: 2^99.69
  (Barbulescu-Duquesne, J. Cryptology 2019, eprint 2017/334; IRTF CFRG pairing-friendly-curves draft: "BN254 ensures no more than
  the 100-bit security level"). Pollard rho on the curve groups is ~2^127. So ~100 bits, dominated by BN254's embedding field.
- Statistical: sumcheck challenges are 125-bit masked values, not full-field (`crates/jolt-field/src/bn254/mod.rs`
  `from_challenge_bytes`: "Legacy convention: a 125-bit masked challenge"). Each round's Schwartz-Zippel term is deg/2^125;
  union over O(10^3) rounds of degree <= ~32 gives about 2^-110 (my order-of-magnitude estimate; Jolt has no soundness
  accountant, and no target is declared). No grinding.
- Hashes: Fiat-Shamir Blake2b (standard, random oracle). No algebraic hash in the default config (Poseidon transcript optional).
- Target and achieved 2^-128: neither. Reaching it needs a >=128-bit pairing curve for Dory (BN/BLS12 with p ~ 461 bits;
  BLS12-381 is ~117-120) AND full-width challenges: protocol changes upstream. => drill-down only for Table 2.

## ICICLE: what it accelerated (survey §4.5 question)
Jolt's ICICLE integration (#503, icicle-jolt fork rev 2441eba, `cuda_backend`) only dispatched G1 MSMs with >64-bit
scalars, i.e. HyperKZG/Zeromorph commitments. It never touched sumcheck, NTT or Dory (Dory MSMs hard-code
`use_icicle=false` at 16763aac). ICICLE's own BN254 MSM/NTT/sumcheck APIs exist, but Jolt never wired them. At the last
rev that has the feature (4c259be477), `--features icicle` does not compile; after my derive patch (`21-icicle-patch.py`)
it fails again at `jolt-core/src/msm/mod.rs:151` (E0308). The CPU build of that rev also panics at runtime
("COMMIT KEY LENGTH ERROR"). The ICICLE CUDA backend library itself built. Verdict: dead path, not worth reviving.
The live curve-Jolt CUDA path is PR #1618 (below).

## VU guest (Rust, like `backends/sp1/guest`)
`evidence/pod-scripts/vu-k1536/`: the guest runs `bare.rs`'s `check_vu` verbatim (K = 1536, A100 BF16 coordinate) over B
VUs passed as one `serde_bytes::ByteBuf`. Rows are synthetic in-domain BF16, because the frozen sets are not on the pod.
- Mode 0 (bare) checks every y[i].
- Mode 1 adds the SHA-256 digest of each 3,072-byte row (`jolt_inlines_sha2`).
- Mode 2 adds the keyed-BLAKE3 digest of each row, frame-v3's keyed row leaf (fixed key; the domain tags are left out).
  It calls the BLAKE3 compression inline directly: 3 chunks × 16 blocks + 2 parent nodes = 50 compressions per row.
  The SDK hasher takes at most 64 B, so `compress_direct` is made `pub` on the pod.
- The host checks the mode-2 digests against `blake3::keyed_hash` (BLAKE3_REF_OK), checks that the proved output equals
  the native output, and verifies every proof.

Cycles, from the tracer's cycle markers on main 922af71c (RV64IMAC cycles plus virtual instructions):

| part | cycles per VU | note |
|---|---|---|
| kernel `check_vu` | 34,092 | 31,928 RV64 + 2,164 virtual; SP1's count is 33,093 |
| bare statement (mode 0) | 43,780 | the extra ~9.7k is postcard input decode and the harness |
| SHA-256 row leaves (2 rows) | 195,005 | 98 compressions, ~1,990 each (hash-bench: ~1,915 per extra block) |
| keyed-BLAKE3 row leaves (2 rows) | 81,536 | 100 compressions, ~815 each incl. the block loop (hash-bench: 649-750) |
| committed, SHA-256 (mode 1) | 239,611 | |
| committed, keyed-BLAKE3 (mode 2) | 126,123 | the survey's pick; ~2.9x the bare statement |

Passing the rows as `Vec<u64>` (v1) cost ~100k extra cycles/VU of varint decode; a byte buffer avoids that.

## Prove times: main, CPU (Ryzen 9 7950X, 16 vCPU), Dory, non-ZK; every proof verified

| B | statement | trace | padded | prove s | verify s | peak RSS |
|---|---|---|---|---|---|---|
| 1 | bare | 45,042 | 2^16 | 4.77 | 0.07 | |
| 16 | bare | 700,440 | 2^20 | 9.5 | 0.11 | |
| 64 | bare | 2,802,135 | 2^22 | 19.0 (24.6*) | 0.20 | |
| 16 | SHA-256 | 3,832,804 | 2^22 | 20.6-21.1 | 0.11 | |
| 64 | SHA-256 | 15,329,461 | 2^24 | 54.5-62.2* | 0.20 | 7.4 GB |
| 16 | keyed-BLAKE3 | 2,018,546 | 2^21 | 13.0 | 0.12 | |
| 64 | keyed-BLAKE3 | 8,071,850 | 2^23 | 30.5 | 0.21 | |

(*) A concurrent build on the pod perturbed the high values; the timing lock covered only runs until 32.
sha2-chain (1000 hashes) proves in 14.25 s.

**ZK (BlindFold, `--features jolt-sdk/zk`), B = 16:** bare 10.0 s against 9.55 s without ZK (+5%); SHA-256 committed
21.6 s against 20.95 s (+3%). Verify takes 0.16 s. All proofs verified. ZK is nearly free in Jolt; only Dory supports it.

## PR #1618 CUDA backend on the 4090 (sm_89, CUDA 12.9 nvcc), `profile --backend cuda|optimized --format none`
Prove time comes from the harness's timed window (witness, commitment, sumchecks, opening). Process wall adds 7-50 s of
CPU tracing and preprocessing (the legacy and modular tracers both run). The harness does not verify proofs; the same
guest and inputs verified on main. The PR's older SDK base traces the VU guest ~18% longer on SHA-256 (281.8k/VU), and
its modular decoder rejects the BLAKE3 inline (`Expansion(UnsupportedInstruction)`), so mode 2 is CPU-only here.

| workload | trace | padded | cuda s | CPU s | speedup | GPU mem |
|---|---|---|---|---|---|---|
| sha2-chain | 0.94M | 2^20 | 1.56 | 4.80 | 3.1x | 1.5 GB |
| sha2-chain | 3.8M | 2^22 | 2.46 | 14.18 | 5.8x | 3.0 GB |
| fibonacci | 3.8M | 2^22 | 2.51 | 13.07 | 5.2x | 3.1 GB |
| sha2-chain | 15.1M | 2^24 | 5.83 | 46.53 | 8.0x | 12.7 GB |
| VU bare, B=64 | 2,902,175 | 2^22 | 5.55 | 17.63 | 3.2x | 3.8 GB |
| VU bare, B=256 | 11,609,243 | 2^24 | 16.77 | 50.01 | 3.0x | 12.8 GB |
| VU SHA-256, B=16 | 4,509,134 | 2^23 | 5.68 | 26.91 | 4.7x | 6.0 GB |
| VU SHA-256, B=48 | 13,531,886 | 2^24 | 9.50 | 54.50 | 5.7x | 14.1 GB |
| VU SHA-256, B=64 | 18,033,352 | 2^25 | 20.56 | 93.88 | 4.6x | 22.1 GB |

- 2^25 is the largest trace that fits in 24 GB. Jolt has no continuations, so a batch larger than one trace becomes
  several independent proofs.
- The bare kernel's trace costs ~2x more per padded cycle on the GPU than sha2-chain or the hashing: 16.8 s against
  5.8-9.5 s at 2^24.
- The PR author's own claim is 3.5x at 2^24 on 1 GPU. We measured 5.7-8x against a 16-vCPU host.

## Projection: 4,096-VU batch (all figures are estimates from the rows above)

| statement | where | proofs | time | per VU |
|---|---|---|---|---|
| bare | 4090 PR #1618 | ~12 of 2^24 (~350 VUs each) | ~3.3 min | ~0.048 s |
| committed SHA-256 | 4090 PR #1618 | ~86 of 2^24 (48 VUs each) | ~13.5 min | 0.198 s |
| committed keyed-BLAKE3 | 4090 PR #1618, if it supported the inline | ~31 of 2^24 (~130 VUs each) | ~5 min | ~0.075 s |
| committed keyed-BLAKE3 | CPU, main | 64 of 2^23 | ~33 min | 0.48 s |
| bare (reference) | SP1, A100 (kb/sp1-prover.md) | 1 | 18.5 s | 0.0045 s |

- Indicative overhead against the 4090's native rate (BF16 dense with FP32 accumulate, 165.2 TFLOP/s, so N = 5.4e10/s):
  bare ~2.6e9x and committed keyed-BLAKE3 ~4e9x on the GPU. SP1's bare A100 figure is 4.59e8x. These are not Table 2
  cells: they cross hardware, and the security filter fails anyway.
- LayerZero's claimed rate (~25M cycles/s per RTX 5090) would prove 4,096 × 126k cycles in ~21 s on one GPU, but that
  code is closed.

## Cost of a full benchmark lane (drill-down only)
Work items:
- Port the guest into `backends/jolt/`: the frozen rows, frame-v3's keyed-BLAKE3 leaf with real domain keys and tags,
  and a native tree check.
- Carry the BLAKE3 inline into PR #1618's modular decoder, or wait for the PR to be rebased or merged.
- Split batches across multiple proofs, run the §Sweep doubling from 1,024 instances, and record buckets for Table 3.

Estimate: 4090 ~4 h ($3) plus an optional H100 hour ($3), ~6-8 agent-hours, about $6 in total. It is blocked on
upstream code that is still a draft.

## Handoffs received
- `20260925T0752Z-handoff-from-coordinator.md` (survey landed). I adopted §4.5:
  - I measured the BLAKE3 inline for the committed guest (126.1k cycles/VU, against 239.6k for SHA-256).
  - I answered what ICICLE accelerates (only HyperKZG G1 MSMs; the path is dead) and gave BN254's ~100-bit level.
  - The survey's "no CUDA in the repo" is right for main. Draft PR #1618 does run on the 4090 (above).
  - The survey's ~63k hash cycles per VU used 96 compressions at 648 cycles each. The measured figure is 81.5k: 100
    compressions at ~815 cycles each, including the loop.

## FINAL
~~~text
tip: lane/jolt-scout @ 7fcedf47 (base main@7fcedf47)  merge-with: none
known-failures: none    pod: terminated 08:07Z; $1.00 (vy-jolt-scout RTX 4090, ~06:46-08:07Z at $0.74/h)
artifacts: art:a53998e6d3c89ac1e579bc974c417f0928f33aad8adea1fa0fa66148c80dbb52
~~~

**Verdict: NO-GO for Table 2.** Curve Jolt misses 2^-128 on both counts: ~100-bit BN254 and 125-bit sumcheck
challenges (~2^-110). Any Jolt result is drill-down only.

| target | CUDA on our GPU | security | ZK | status |
|---|---|---|---|---|
| (a) curve Jolt + ICICLE | dead: only HyperKZG MSMs, removed 2025-07/08, last rev doesn't compile. Draft PR #1618 native CUDA builds and runs on the 4090 (5.7-8x CPU at 2^24, max 2^25) | ~100-bit comp., ~2^-110 stat. | BlindFold, +3-5% | measured |
| (b) lattice Jolt (Akita) | no CUDA code (Metal draft only) | not assessed | none | skipped (user rule) |
| (c) LayerZero Jolt Pro | closed source | n/a | "roadmap" | not runnable |

- Guest cycles/VU: kernel 34.1k; committed 126.1k with keyed-BLAKE3 leaves, 239.6k with SHA-256.
- Prove times: CPU B=64 keyed-BLAKE3 takes 30.5 s (verified). The 4090 cuda backend runs B=48 SHA-256 in 9.5 s.
- 4,096-VU projection on one 4090: bare ~3.3 min, committed ~5-14 min, as multiple proofs. SP1 bare on an A100 is 18.5 s.
- The handoff `lanes/coordinator/20260925T0810Z-handoff-from-jolt-scout.md` recommends no-go now. It describes an
  optional `jolt-drilldown` lane (~$6, 6-8 agent-hours), triggered when PR #1618 merges.
- Durable facts are in `kb/jolt-prover.md` (new; listed in `kb/README.md`).
- Not done:
  - An A100/H100 run: it would not change the verdict.
  - Keyed-BLAKE3 on cuda: PR #1618's decoder rejects the BLAKE3 inline.
  - The real frozen rows: the rows were synthetic in-domain BF16.
