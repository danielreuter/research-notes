---
lane: flock-gpu-link
kind: report
created: 2026-09-25T17:35Z
status: open
---

CHECKPOINT b684b12 (17:44Z) [open] design: GPU L4 as leaf-per-block BlockR1cs (k_log 20, 48 compressions/leaf, chain = copy rows, lincheck = 2^14 fold x eq_hi + sparse delta; no wiring GKR, ~240 coin RTs vs 1070); L2 = N-claim ring-switch batch. Writing scope doc
CHECKPOINT none (17:38Z) [open] read brief/contract/kb/red-team; ref: B-Ligero H100 BF16 keyed-BLAKE3 3.64 s/4096 (2.86e8x); cell A100 prime 2.7 s, Flock 20.7 s of which 16.3 s = 1070 coin RTs @15 ms. Next: Flock-CUDA code read, scope doc
CHECKPOINT f7de4620 (17:35Z) [open] started: scoping GPU route (a) L2/L4/L3 + live-coin model; agent bc-9209cb00-14e7-59ad-85aa-682c82ad797a
