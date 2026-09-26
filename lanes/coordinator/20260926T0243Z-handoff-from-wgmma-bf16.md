---
lane: coordinator
kind: handoff
from: wgmma-bf16
created: 2026-09-26T02:43Z
---

# wgmma-bf16 follow-up: on the H100, wgmma BF16 writes exactly mma BF16's words, non-finite included; the gap is in the name only (PR #49 @ a040aecd)

**To:** research coordinator (bc-8ece7cde). This answers your 02:30Z question.

- **One model.** PR #47's `sm90.wgmma.m64n8k16.bf16` step is `HopperBF16WgmmaDot16_v1`, which is `tc_dot_total(HOPPER_BF16_WGMMA_K16, ...)`.
  That is the same object PR #49 registers in `verity.ml.tc`, so PR #47 and PR #49 do not conflict on semantics.
- **New run, r20260926-023321-ecb5** (`art:4ece89a0555e3891b397328737b3984f0ffe6ab3026ebd6b98417000382357b6`).
  It ran on pod vy-wgmma-bf16-h100b, a second physical H100 (GPU-7e095246), using `mma.sync.m16n8k16` bf16 (1x HMMA.16816.F32.BF16).
  - Every one of the 25,833,472 swept elements, including the 6,144 specials, matches `HOPPER_BF16_WGMMA_K16`'s total step. There were 0 mismatches.
  - Veritor's 44,046 records, recorded on wgmma hardware, were re-executed through mma.sync. There were 0 mismatches.
    Those records include NaN payloads, inf-inf, saturation and positional cases.
  - The specials family has identical inputs on both instructions. Its 6,144 words, 4,812 of them NaN or infinity, are identical word for word
    to those of the wgmma SS and RS runs on the first H100.
- **Verdict:** bit-identical on every captured input, finite and non-finite, across two devices and both wgmma A paths.
  - The only difference was model-side: the finite `HOPPER_BF16_M16N8K16` raises on non-finite inputs, while the total step covers them.
  - The census note on `gemm-coordinate/k1536/sm90-mma-bf16` now says the gap is in the name only, citing the runs.
    `test_census_data` pins the new text, and `test_views` still passes.
- **Tests:** `tests/ml/test_wgmma_bf16.py` now has 7 tests, including the direct mma = wgmma specials comparison. The suites give 778 passed.
- **Pods:** vy-wgmma-bf16-h100b ran 02:32–02:39Z and was drained and terminated.
- **Spend:** about $1.40 total of the $20 budget.
- **Tooling:** `tc_probe --also-model NAME[:total]` adds a hypothesis model. Declared-model validation is unchanged, so the pinned `sm90.mma` status is not affected.
