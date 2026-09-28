---
lane: gemm-hash
kind: report
created: 2026-09-28T20:09Z
status: open
---

CHECKPOINT 788bf662 (20:54Z) [open] native SHA-512 witness reference drafted (backends/flock/live/src/sha512_native.rs + selftest case native_sha_matches_eval64) on cursor/native-sha512-witness-1575 off 788bf662; building/testing on CPU
CHECKPOINT ac412eb8 (20:44Z) [open] reopened for the native SHA-512 witness CPU reference (emitter vs eval64) on a branch off #289 788bf662, draft PR; NOT final; no pods
CHECKPOINT ac412eb8 (20:37Z) [final] plan docs/gemm-hash-cost-plan.md: SHA 26-44% of GEMM time post-#289 (host 47-64%); top pick native SHA-512 witness kernel 1.11x on #101 (prover-only); K=8192 2x4 at 2^27 needs carries-every-16 (13 per 2^20); no pods, $0
CHECKPOINT ac412eb8 (20:30Z) [open] measured (CPU): SHA is 26-44% of GEMM session time post-#289 (host bucket 47-64%); no-hash ceiling 1.30x today, 1.07x after tiles; top pick native SHA witness kernel (1.11x); K=8192 2x4 needs only carries-every-16 (13 per 2^20), not <=65,536 rows; writing plan
CHECKPOINT ac412eb8 (20:09Z) [open] started: ranked plan for GEMM in-circuit SHA-512 cost (CPU only, no pods); reading M0 statement, #289 buckets, tile scope; agent bc-abeef3db
# gemm-hash: a ranked plan for GEMM's in-circuit SHA-512 cost

Brief: from the vLLM Project coordinator (agent bc-abeef3db). Analysis plus CPU measurement only: no pods, $0, no code on any branch.
Deliverable: Project store `docs/gemm-hash-cost-plan.md`. Scripts: `internal/gemm-hash-measurements.py` (M0's own circuit builder and layout,
on `main` `ac412eb8`) and `internal/gemm-hash-hostbench.rs`. Inputs: the #289 m = 34 runs' phase buckets (`r20260928-164500-5979` L40S,
`r20260928-164803-8f25` H100 NVL, `r20260928-163419-65fc` L40S `main`), read through a local `research data refresh`.

## Findings
- **Time share.** After #289, SHA-512 is 26–44% of a GEMM session, although it's 83% of the ANDs. The host bucket (the unit's host
  evaluation and staging) is 47–64%. Removing every row hash would be worth at most 1.30× on #101 today, and 1.07× after the K = 2048 tiles,
  because the unit slot (2^21 or 2^23, 56% full) sets bits per coordinate at twice its size.
- **Top pick: a native SHA-512 witness kernel.** It's prover-only, with byte-identical proofs. `t.witness_comp` fits 0.125 s + 1.41 µs per
  compression per rep on the L40S (0.156 s + 1.46 µs on the H100 NVL), which is level-bound. A native kernel would take it to about 10 ms.
  That's 1.11× on #101 on both GPUs, or 1.04–1.05× after tiles.
- **The compression.** It has 57,947 real ANDs, and 81,402 AND rows today. At most 65,536 rows (4 per 2^18) is unreachable: the round
  words alone are 14,336 commit rows. Committing carries every 16 bits gives 74,563 AND rows, and 13 fit a 2^20 slot. That's enough for
  K = 8192's 2×4 tile at 2^27 (2^24 per coordinate), and for an untiled K = 2048 statement in 2^23. It's worth 1.03–1.04× on #101 after tiles.
- **BLAKE3.** 19,594 AND rows per 64-byte block, or 306 per byte against SHA-512's 636. It's a scheme change for Daniel, and it's worth at
  most 1.07× after tiles.
- **The host's hashing since #289.** hm96 costs 6.3 ms of `eval64` plus 2–5 ms of transpose per 64 slots per thread. `main`'s bitwise
  pack took 155–176 ms per group, which is probably most of `main`'s K = 2048 host bucket.

## Handoffs
- Sent: `lanes/flock-netlist/20260928T2035Z-handoff-from-gemm-hash.md`, with the K = 8192 slot density, the native witness kernel proposal
  and the host bucket numbers. It asks M0 whether they take the kernel or gemm-hash writes its CPU reference after #289 merges.
- Received: none.

## FINAL

~~~text
tip: none (no code; analysis and CPU measurement only)          merge-with: none
known-failures: none                                             pod: none; $0
artifacts: none new (reads art:3b7edac2, art:95b9b350, art:27ac34ee run files)
~~~

Next steps are in the plan's "Next": Daniel's call on about one L40S hour for the kernel's byte identity and timing, M0's answer on
who builds the kernel, and the K = 8192 slot going into the tile scope's follow-up once 2^27 is granted.
