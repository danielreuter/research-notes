---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T21:40Z
---

# Two jobs for 01:00Z (after your FINAL): (1) re-label route (a) art:4b52879f (my 2145Z); (2) verify the H100 keyed-BLAKE3 x4 cells art:d88a9948 (fp8, 65,536) and art:5ea60c40 (bf16, 16,384)

(2) Producer: x4-hopper-blake3 (handoff `lanes/coordinator/20260925T2112Z-handoff-from-x4-hopper-blake3.md`), pinned tree
9a78cd68 (the PINS are on main since 7da00370). Reverify each result from its proofs tree (fp8 art:d5a814d7, bf16 art:f200431e)
and label `verified accepted`. Rule I: check the plateau equivalence docs on a fresh pod, fp8-hopper-x4 65,536 art:a400cae2 and
bf16-hopper-x4 16,384 art:6b27220a (raw files in the runs' outputs/, --vus = the doc's own n), and label them. Order: (1), then (2).
Both by about 00:30Z. These replace today's x1 H100 keyed-BLAKE3 cells (2.8e8x) with 1.5e8x.
