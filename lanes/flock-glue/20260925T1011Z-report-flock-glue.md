---
lane: flock-glue
kind: report
created: 2026-09-25T10:11Z
status: open
---

CHECKPOINT ba852261 (12:10Z) [open] H=2 witness (64 VU/CTA) bit-exact but no gain on H100 BF16 4096 (devovl 0.1673 vs H=1 0.1683, dev run); keep H=1. Final runs A100 r20260925-114930-2278, H100 r20260925-114930-aed8 preserved. Wrapping up: pods drain, report, handoff.
CHECKPOINT 78b1a62e (11:51Z) [open] final recorded runs launched: A100 r20260925-114930-2278 (ampere_bf16), H100 r20260925-114930-aed8 (hopper bf16+e4m3): before/devwit/devgpu/devovl x 1024/4096 (Flock b684b12 default ~2^-100) + flock-128-r2 cost (Fast100 x2) + nsys per-batch kernel time. Found: GPU grind cutoff 8 bits (host below) halves idle GPU gaps; side-stream witness overlap -19 ms A100, ~0 H100 at 4096 (SM contention), -25 ms H100 at 1024. Witness kernel knobs flat (~25 ms@64VU H100): per-level latency bound.
CHECKPOINT ac2a497 (11:20Z) [open] recorded runs r20260925-111311-dc17 (A100) / -250b (H100), Flock b684b12 default ~2^-100: 4096 VUs prover wall before->devgpu: A100 bf16 0.871->0.302 s (3.67x->1.27x bare), H100 bf16 1.033->0.195 (9.1x->1.72x), H100 fp8 0.485->0.114 (6.9x->1.61x). Building mode 3 (side-stream witness overlapping BLAKE3 proof). flock-128 handoff 1055Z received: r2 = 2x Fast100, will re-time.
CHECKPOINT none (11:04Z) [open] A100 4096 VUs ampere_bf16 (Flock b684b12 ~2^-100 profile): device witness + GPU PoW grind -> FFI sum 0.302 s = 1.27x bare (host grind 0.626 s); harness rebuilt BLAKE3 R1CS per call (~1 s), now cached; witness kernel 46 ms latency-bound, profiling per-segment critical path. H100 pod oypxgunobip13f up.
CHECKPOINT 5e21eead (10:53Z) [open] device unit witness bit-exact on 3 pipes (64 VUs); batched kernel 47.6 ms@64VU ampere, profiling latency now; host PoW grind identified as 0.06-0.11 s/proof host glue; handoff 20260925T1020Z acted on: every timing labelled Flock b684b12 profile (~2^-100 campaign accounting, 16-bit PoW credit, GF(2^128)). Next: A100 bench 1024/4096, H100 pod.
CHECKPOINT a19aacb (10:37Z) [open] A100 pod 56nan0h04ho1u9 up; wrote device unit-witness kernel (bit-sliced chained VUs, level-parallel) + FFI patch (GPU PoW grind, phase timers, per-circuit CSC cache); building+bit-exact check run r20260925-103733-28ee
CHECKPOINT none (10:11Z) [open] started: reading contract, flock-bench-80gb/flock-bench reports; next: plan device-side unit witness + pods
