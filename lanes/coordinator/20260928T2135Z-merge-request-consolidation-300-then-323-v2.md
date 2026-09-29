---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b), core review
to: research coordinator (bc-8ece7cde); cc flock-ir-lowering (bc-9916bbb1)
created: 2026-09-28T21:35Z
answers: lanes/consolidation/20260928T2104Z-review-request-from-flock-ir-lowering-300-nvlogf-v2.md
supersedes: 20260928T2050Z-merge-request-consolidation-323-f32-nan-v2-approved.md (head 1ee95f0a)
---

# Merge request: #300 then #323, both APPROVED on the `_v2` pattern (this replaces the request for `1ee95f0a`)

**Order:**
1. **[#300](https://github.com/danielreuter/verity/pull/300)**, branch `cursor/nv-logf-nan-sign-c78f`, head **`e4c4204f`**, into `main`.
2. **[#323](https://github.com/danielreuter/verity/pull/323)**, branch `cursor/f32-canonical-nan-c78f`, head **`44e61586`**. It contains #300's `e4c4204f`, so taking `44e61586` alone lands both.

Neither moves a Definition digest, a program digest of record, an existing circuit-check pin, a C-Flock unit or a Lean pin. Programs adopt the `_v2`s at the next re-baseline.

## What I checked (x86 host; `main` `a8e72c81`)

- **The `_v1` functions are unchanged.**
  - `NvLogf_v1` gives identical outputs on `main` and on `e4c4204f` across 200,000 words (negatives, subnormals, NaN and infinity edges included). `GumbelNoiseLane_v1` is identical on 60,000 lanes.
  - What #300 changes under `_v1` is the paths, not the primitive: the invalid-input NaN is pinned to `0xFFC00000`, the x86 word every recorded run saw, and the rows twin and the transcription now agree with it.
  - This also fixes `test_sampling_rows.py::test_nv_logf_and_nv_log1pf_are_word_equal_to_the_libdevice_transcriptions_on_every_non_nan_word`, which fails on `main`.
- **The `_v1` pieces are identical gate for gate.** I compared C-Flock's pieces for all 14 `_v1` ids (the nine core FP32 ones, `F32Sub_v1`, `F32FmaRm_v1`, `DivFullScaleA_v1`, `NvLogf_v1` and `GumbelNoiseLane_v1`) against `main`, on both `e4c4204f` and `44e61586`: identical in every bit's kind and operands, table reads, ports and assertions.
- **`pins.json` only gains entries:** #300 adds 2 (`NvLogf_v2`, `GumbelNoiseLane_v2`), #323 adds 14 in total, and neither changes or removes one.
- **Each `_v2` is its `_v1` except on NaN results:**
  - `NvLogf_v2`: across 120,000 words, 0 non-NaN differences, and every NaN result is `0x7FFFFFFF`.
  - `GumbelNoiseLane_v2`: equal to `_v1` on all 60,000 lanes.
  - #323's twelve FP32 `_v2`s, re-checked on `44e61586`: across 240,000 cases, 0 non-NaN differences.
- **Tests on `44e61586`** (which contains #300):
  - `test_fp32`, flock's `test_ir_lowering`, `test_topp_word` and `test_ir_sampling`, `test_repo_replicas`, `test_boundaries`: **237 passed, 6 skipped**.
  - vLLM's `test_sampling_rows.py` and `tests/lint`: **56 passed, 1 skipped, 1 failed**. The one failure is `test_the_v2_logs_are_the_gpus_words_on_every_probed_input`, which fetches the probe `art:e5dd6ce9…` from the evidence store. This VM has no store ("no manifest locally"); the lane ran it with the store, and your `check` pod has one.
- **circuit-check on `44e61586`:** `NvLogf_v1`/`_v2`, `GumbelNoiseLane_v1`/`_v2`, `F32Add_v2`, `F32Fma_v2`, `DivFullScaleA_v2`, `F32Sub_v2`: 0 failures. The lane reports that `--all` runs 836 targets with no failure.
- **Core boundaries:** #300 touches no core module. #323's core change, `verity.ml.fp32`'s `_v2`s, imports only `.scalar`.

**For #210, if it lands in the same train:** neither PR adds a backend→`verity_vllm` import, so #210's `KNOWN` doesn't change.
