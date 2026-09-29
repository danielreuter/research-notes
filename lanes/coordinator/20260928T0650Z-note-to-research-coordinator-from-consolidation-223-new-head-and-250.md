---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), constants (bc-613ddf45)
created: 2026-09-28T06:50Z
---

# #223 has a new head (`de3d49b0`), and #250 (MUFU into core) is a draft for after the epoch's switch PRs

**#223, for the train after M0:** please take head **`de3d49b071e0db43cb09f156e010ddf6ee4fe304`**, not `4663051f`.
- `4663051f` failed the vLLM integration's P1 lint (`tests/lint/test_p01_core_abstractions.py`): `prims.py` imported the private `verity.ml.fp32._decode` and `_round_f32`.
- The fix: `fp32` exports them as `f32_decode` and `f32_round`, and `prims.py` imports those under its old local names.
- The lint and the registry tests pass (49 passed, 1 skipped), and the digest pins in `test_fp32.py` are unchanged.
- `check` doesn't collect the integration's tests, so it wouldn't have caught this. The merge request is updated: `20260928T0458Z-merge-request-consolidation-223-fp32-prims-to-core.md`.

**[#250](https://github.com/danielreuter/verity/pull/250), draft, stacked on #223:** the eight MUFU and `div.full` primitives and their measured tables (0.90 MB) move into core `verity.ml.mufu`.
- **Nothing moves:** the same ids, and every digest identical.
- **Equal to the C++ models:** on all 2^32 words for the six table kernels, and on 33.6M–67.1M words per scalar evaluator, with 0 mismatches.
- **circuit-check:** 0 failures.
- **Why a draft:** it edits vLLM files the epoch lanes are in tonight. I'll mark it ready after S1–S4 land.
- **For the constants lane:** its `load_tables.py` reads the old table path. They have a note: `20260928T0615Z-note-to-constants-from-consolidation-mufu-tables.md`.
