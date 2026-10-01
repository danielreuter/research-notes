---
id: 20261001T0000Z-handoff-from-proofs-composites-done
campaign: verity
lane: proofs-tc-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# STOP: the FP8/FP4 GemmCoordinate composites are already done (proofs-gemm-defs `21e333a9`, circuit-check green); don't write them

Your 4:51 PM PDT checkpoint says "next: FP8/FP4 GemmCoordinate composites". That would duplicate them. The composites landed on
`cursor/proofs-gemm-defs-95d4` (`0f05a4dd` the MXF4 step, `21e333a9` the three coordinates), with ids in
`lanes/proofs-gemm-defs/NAMES.md`. Keep to the probes: the E5M2 anchor (your `BlackwellE5m2QmmaDot32_v1` is fine), the
NaN/Inf semantics, and the MXFP4 edge probe (sky job 346). Push your branch.
