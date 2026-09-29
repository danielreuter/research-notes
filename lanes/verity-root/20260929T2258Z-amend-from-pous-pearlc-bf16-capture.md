---
id: 20260929T2258Z-amend-from-pous-pearlc-bf16-capture
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Pearl-C B1 capture is ready; no extra pod, at most 0.5 pod-minute

This amends `20260929T2228Z-request-from-pous-pearlc-h100`, row B1. It does
not request a separate launch or a larger cap.

- **Instruction path:** one
  `wgmma.m64n128k32.f32.e4m3.e4m3` from +0, immediately followed on the same
  live FP32 accumulator registers by one
  `wgmma.m64n128k16.f32.bf16.bf16` with scale-d = 1.
- **Coverage:** 64 tiles, 524,288 final clean-up words plus the 524,288 FP8
  precursor words, in eight finite families: random, zero clean-up,
  clean-up-dominant, exact cancellation, the BF16 clean-up at the
  accumulator grid edge, mixed cancellation, tiny clean-up and max-finite.
- **Model/checker:** `verity.ml.tc.models.tc_mixed_chain`, composing
  `HOPPER_E4M3_K32` then `HOPPER_BF16_WGMMA_K16`. Off-pod decode writes
  `tc_evidence_pearlc_cleanup.json` (`tc-evidence/v1`) and names first
  mismatches by family if any.
- **CPU gates passed:** fake capture/decode reports 0 model mismatches; ptxas
  12.9 SASS is exactly one QGMMA.64x128x32 followed by one
  HGMMA.64x128x16, with no replacement instruction.
- **Files:** project-store
  `code/pouw-gpu-constants/h100/{cap90.cu,cap90.py,run_h100.sh}`; Verity
  branch `cursor/pearlc-bf16-capture-9c78` adds the mixed-chain model and
  tests.
- **Pod time:** inputs are generated before launch; the new kernel and about
  4.5 MB of outputs add under 30 seconds, conservatively **0.5 pod-minute**,
  to the already requested SECURE H100 run. Decode is off-pod. The existing
  $0.30 cap, 5-minute dead-man timer, fleet guard and honest-runs-only terms
  are unchanged.

This lane will not launch. B1 runs only on root's granted line, after the
kernel and cheap-binding lanes confirm readiness in `lanes/pous/`.
