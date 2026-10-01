---
id: 20261001T0738Z-report-proofs-flock-fp
campaign: overnight
lane: proofs-flock-fp
kind: report
status: open
repo: verity
origin: proofs-flock-fp (bc-15199603-ae1e-5aa0-9da4-6be8dedb83e6)
---

FP hill-climb (E4M3, NVF4, MXF4), newest first. Each step is a byte-identical point against the format's clean step 0 at the
same K; a gain under 20% is re-run once (clean FP4 samples spread 12-19%). Branch `cursor/proofs-flock-fp-95d4`.

CHECKPOINT cde1c7ac1 (07:38Z) [open] 12:38 AM PDT: step 1 (column-major verifier fold, bf16-hill d1775df80) E4M3 K=16384 4.49e8 vs step 0 7.23e8 (-38%, verify 11.4 -> 6.6 s/statement), clean, r20261001-072900-9fd9. NVF4 and MXF4 K=16384 running; step 2 (overlap, ea4513262, binary 557b507079078cc7) synced as tree proofs-flock-fp-s2, its staging next.
