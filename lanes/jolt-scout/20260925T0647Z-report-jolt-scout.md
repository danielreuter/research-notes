---
lane: jolt-scout
kind: report
created: 2026-09-25T06:47Z
status: open
---

CHECKPOINT 9bfc8e2 (07:31Z) [open] 07:31Z: 4090 pod up. VU guest: kernel 34.1k cyc/VU, SHA-256 rowhash 195k/VU; B=16 committed CPU prove 26.4s valid. ICICLE path dead (removed #822, last rev broken). PR1618 CUDA built sm_89/nvcc12.9, sweep queued. ZK build running. Lattice/LayerZero: no CUDA/closed.
CHECKPOINT 00ffe398 (07:08Z) [open] Dory+ICICLE never coexisted (Dory hard-codes use_icicle=false @16763aac); PR#1618 = curve/Dory CUDA draft, not lattice; Akita lattice: no CUDA, no zk; Jolt Pro closed. Building main VU guest (bare kernel verbatim) + old ICICLE rev on 4090
CHECKPOINT 7fcedf47 (06:47Z) [open] startup: jolt main has no ICICLE (removed #779 2025-07-15/#822 2025-08-01; README 'pre-alpha, do not use' since #730); Akita lattice PCS merged 09-15, PR#1618 still draft; pod vy-jolt-scout 4090 up; next: build icicle rev 4c259be4 + main on pod

# jolt-scout: can Jolt (a16z) be a Table 2 backend? (feasibility scout)

Status: IN PROGRESS (draft written 07:30Z; FINAL section below when done). Pod vy-jolt-scout (RTX 4090 24 GB, Ryzen 9 7950X
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
