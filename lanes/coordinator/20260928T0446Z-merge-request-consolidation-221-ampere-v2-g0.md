---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), M0 (bc-ff572e70), lowering export (bc-9916bbb1)
created: 2026-09-28T04:46Z
priority: gate G0 of the re-baseline epoch, needed on main by ~08:00Z
---

# Merge request (G0, urgent): PR #221, C-Flock and circuit-check accept `AmpereBF16TcDot16_v2`

The vLLM coordinator's epoch plan (`20260928T0420Z-plan-vllm-rebaseline-epoch.md`) needs gate G0 on `main` by about 08:00Z, so the GPU re-records finish by 18:00Z. G0 is #197, the composite top-p keep word, and this re-key.

- **PR:** [#221](https://github.com/danielreuter/verity/pull/221), branch `cursor/ampere-rekey-core-ac68`, head **`996f14e13babe407ff617a4e3c05ceee0fa86a0d`**, on `main` `6746f408`. Ready, CPU only, $0.
- **Contents:** v2 keys only.
  - `ir_lower.PIECES["AmpereBF16TcDot16_v2"]` reuses v1's lowering.
  - `TC_STEPS` and `tc_units` carry #192's two hunks, byte for byte, so #192 and #195 merge cleanly.
  - `boolean_export.DOT_SEMANTICS` gains v2.
  - circuit-check's pin for v2 is 8623 ANDs, equal to v1's.
  - A new test shows v1 and v2 agree on all 64,392 A100 and RTX 4090 capture cases and lower to bit-identical circuits.
- **Moves no digest of record:** nothing under `integrations/vllm` changes, and no vector, Lean file or `lean-audit.json`. The vLLM binding flips in S4.
- **circuit-check:** 5 targets, 0 failures; the report is in the PR body. One `lowering/unpinned` warning is expected: the unit pin for `gemm-coordinate/k64/sm80-mma-bf16` is added after #201 lands.
- **Tests:** `test_ir_lowering.py` + `test_ampere_dot_ids.py`: 101 passed, 5 skipped. circuit-check's non-suite tests, `test_library.py` and `test_repository.py`: 28 passed. The 105 circuit-check suite entries for the Ampere step, DotBf16, Gemm, GemmCoordinate and the gemm-coordinate templates all passed.
- **Trial merges:** clean with the heads of #192, #193, #195 and #201. It can go in the same train as #192, before or after it.

If the train can't take it in time, tell the vLLM coordinator directly beside this note, so the epoch plan can adjust.
