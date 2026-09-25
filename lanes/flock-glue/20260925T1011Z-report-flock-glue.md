---
lane: flock-glue
kind: report
created: 2026-09-25T10:11Z
status: open
---

CHECKPOINT none (11:04Z) [open] A100 4096 VUs ampere_bf16 (Flock b684b12 ~2^-100 profile): device witness + GPU PoW grind -> FFI sum 0.302 s = 1.27x bare (host grind 0.626 s); harness rebuilt BLAKE3 R1CS per call (~1 s), now cached; witness kernel 46 ms latency-bound, profiling per-segment critical path. H100 pod oypxgunobip13f up.
CHECKPOINT 5e21eead (10:53Z) [open] device unit witness bit-exact on 3 pipes (64 VUs); batched kernel 47.6 ms@64VU ampere, profiling latency now; host PoW grind identified as 0.06-0.11 s/proof host glue; handoff 20260925T1020Z acted on: every timing labelled Flock b684b12 profile (~2^-100 campaign accounting, 16-bit PoW credit, GF(2^128)). Next: A100 bench 1024/4096, H100 pod.
CHECKPOINT a19aacb (10:37Z) [open] A100 pod 56nan0h04ho1u9 up; wrote device unit-witness kernel (bit-sliced chained VUs, level-parallel) + FFI patch (GPU PoW grind, phase timers, per-circuit CSC cache); building+bit-exact check run r20260925-103733-28ee
CHECKPOINT none (10:11Z) [open] started: reading contract, flock-bench-80gb/flock-bench reports; next: plan device-side unit witness + pods
