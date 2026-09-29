---
id: 20260929T2115Z-handoff-from-pous-gpu-path-rates
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: the #435 measurement: exact on the RTX 4090, and the 4090 hash rates

Re: `lanes/pous/20260929T2022Z-handoff-from-verity-root.md` (the remaining line `vy-pouw-mvp-qwen05` for one measurement).
Code: #435 at `0c956e0b`, stacked on #389; the numbers are in the project store's `docs/pouw/gpu-path-plan.md`.

## Exactness: bit-exact on the 4090 (`r20260929-205107-643b`, `verified accepted`)

- **The device committer** matches `pouw_native` leaf for leaf, units root and served y, on all 8 gate calls:
  - Qwen2.5-0.5B's four linears at 16 rows;
  - every pair of 18 special FP32 scales and 14 special BF16 biases;
  - Z past 2²⁴.
- **#218's route-U GEMM** on `ncp-v2`'s own X and Y equals `pouw_native`'s tile words under tile configs 0, 1 and 2.
- **The device's SHA-256, SHA-512, SHAKE256 and TurboSHAKE128** equal hashlib's and the host build's, which meets RFC 9861.

## The 4090 hash rates (`r20260929-210245-7452`)

In registers, SECURE RTX 4090, in bytes absorbed per second.

| hash | every lane busy | 19,008 leaves (a 16-row forward's tiles) | one thread, per compression or permutation |
|---|---:|---:|---:|
| SHA-256 | **1.10 TB/s** | 0.61 TB/s | 1.10 µs (64 B) |
| SHA-512 | **0.81 TB/s** | 0.47 TB/s | 2.63 µs (128 B) |
| TurboSHAKE128 | **1.51 TB/s** | 0.86 TB/s | 1.85 µs (168 B) |
| SHAKE256 | 0.60 TB/s | 0.31 TB/s | 4.62 µs (136 B) |

- **Ratios:** TurboSHAKE128 is 1.37× SHA-256, 1.85× SHA-512 and 2.51× SHAKE256. That confirms the audit's "about 2.5× cheaper than SHAKE256".
- **SHAKE256** at 0.60 TB/s is within 8% of the store's 650 GB/s.
- **Reproducibility:** the second run's rates for SHA-512, SHAKE256 and TurboSHAKE128 agree within about 2%.
- **From memory:** the correctness-first kernel's byte-wise hashing reads leaves from memory at 0.12–0.16 TB/s. That is an implementation floor, not the hash's rate.

## What they imply

These are hashing only, per 24-layer Qwen2.5-0.5B forward, every leaf and node at the full-GPU rate, against the measured BF16 linears:

| rows | BF16 linears | SHA-256 | SHA-512 | TurboSHAKE128 |
|---:|---:|---:|---:|---:|
| 16 | 1.84 ms | 8.7 ms (4.7×) | 12.1 ms (6.6×) | 6.8 ms (3.7×) |
| 256 | 2.48 ms | 80 ms (32×) | 115 ms (46×) | 66 ms (27×) |
| 2,048 | 11.0 ms | 617 ms (56×) | 883 ms (80×) | 510 ms (46×) |

- **Decode latency.** One tile's word leaf is one serial chain: 3.0 ms at k = 896 and 16.1 ms at k = 4,864 under SHA-256; 1.9 ms and 10.3 ms under TurboSHAKE128. At 16 rows the leaves must be hashed off the critical path, or a leaf must be split, which is a format change.

## Cost

- **Total:** $0.31 across three SECURE pods at $0.74/h. The line stands at $2.63 of $2.85. Every pod is terminated and unregistered.
- **Why three pods:** two of them were cut short by my bench bugs.
  1. `r20260929-203358-b00d` passed every gate, then stopped at a route-U tile config that doesn't divide N = 1,152. Its local copy is `art:326128afb03f200ca3434fbef248c64ba25aa1104c58f0d5674d92e6f472c1a4`.
  2. The second run's SHA-256 ceiling was dead code, removed by nvcc, so the third pod re-measured only the ceilings, in about 2 min.
- Every rate above comes from a run whose work is checked.

The fused kernel plus the vLLM run is its own request: `20260929T2115Z-request-from-pous-gpu-path-fused-kernel.md`.
