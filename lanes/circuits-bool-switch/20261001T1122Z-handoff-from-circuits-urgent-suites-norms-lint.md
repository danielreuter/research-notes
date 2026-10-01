---
id: 20261001T1122Z-handoff-from-circuits-urgent-suites-norms-lint
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits, URGENT for PR 1 (4:22 AM PDT): your suites run never ran, and the b1 norms on your head may fail the vLLM lints

1. **Suites run `r20261001-102007-6531` failed at launch** (rc 2): `error: Extra torch-cpu is not defined in the optional-dependencies table for
   verity-check` (its `out/suites.log`). No suite ran. Re-launch from the repo root the way AGENTS.md says (`uv sync --all-packages --extra
   torch-cpu`, then `uv run tools/check/suites.py`), or as `check --record` on the final head.
2. **The b1 norms (`boolean_norms.py`, SmolLM2's, in PR 1) on `31ef5e28b` still assign `.word` after construction** (lines 178, 517, 619).
   circuits-bool-norms found the vLLM lint reads those as P9 runtime patches. It also found a P1 core-private `trace._body` use, and an
   `_on_word` TypeError with proofs' Boolean MUFU. Its fixes:
   - `8a1a80f5e` (`trace.emit`): `boolean_norms.py` only;
   - `2acad3c94` (word view at construction): `boolean_norms.py` + `boolean_dense_norm.py`; take only the `boolean_norms.py` half;
   - `b376087ec` (`_on_word` fix): `boolean_norms.py` + `test_boolean_norms.py`.
   Take these into PR 1 **without** `boolean_dense_norm.py`, which still carries the eight ids `boolean_dense` owns. Check that the norms' pinned digests don't move.
3. **Torch frontend ambiguity:** circuits-bool-norms saw 21 frontend failures and 8 collection errors when a module `catalog.load` imports pulled in
   `verity.ml.boolean.gemm`: its `AmpereBF16TcDot16_v3` made the frontend's unversioned `AmpereBF16TcDot16` ambiguous (their `55fa55417`).
   `boolean_attention.py` on your head imports `verity.ml.boolean.gemm as BG`. Run the vLLM frontend tests and the lints on your head now.
   If they fail, fix it before the hand-off (proofs owns `gemm`, so ask proofs in lanes/proofs-ir/ if the fix is theirs).

Say in the hand-off which of these you fixed and how the suites came out.
