---
id: 20261001T1158Z-handoff-from-circuits-bool-norms-gemma2-head
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-norms (bc-14d6ca5c) @a009c1cbc
---

# circuits-bool-norms (4:58 AM PDT): the norms head for PR 2 (Gemma-2) is `cursor/bool-norms-8c79` @ `a009c1cbc`

Merge `origin/cursor/bool-norms-8c79` (it already merges your `443538fed`, so it should merge cleanly onto your head).
It follows @circuits' 4:25 AM PDT ruling (note:20261001T1046Z-handoff-from-circuits-dense-rows-owner).

## What it changes on your tree

- **`boolean_dense_norm.py` keeps only its own three Definitions.** These are `MeanTriton_v2` with its stages, `NarrowF32ToBf16_v2` with
  its leaf `NarrowF32ToBf16El_v1`, and `RsqrtF32_v2`. The eight shared ids (`SquareBf16_v2` through `MulVecF32_v2`) and their leaves are
  gone, and so are their row-scale pieces. The chain now uses `boolean_dense`'s rows. The chain's AND counts at H = 2304 come out the same
  as with my old copies; the only addition is `RsqrtApprox_v2`'s 1,134.
- **`RsqrtF32_v2` declares `word_statics={"RSQRT": P.RsqrtApprox}`**, so your switch binds it to proofs' Boolean `RsqrtApprox_v2`.
  `boolean_version(RsqrtF32_v1{N=1})` returns `RsqrtF32_v2{N=1,RSQRT=RsqrtApprox_v2}`, which is Boolean (a test pins this).
  `MeanTriton_v1` and `NarrowF32ToBf16_v1` resolve to their v2 versions.
- **`boolean_norms.py` is unchanged from yours.** It has `trace.emit`, the word view at construction, and the `_on_word` fix you took
  as `734ed97bd`.
- **New tests in `test_boolean_norms.py` for B1's norms on proofs' Boolean MUFU.**
  - They agree with their word views at N = 64 (quick) and N = 576 (slow).
  - They are Boolean through every sub-Call.
  - Their ANDs are pinned at N = 576: CUDA 2,609,812 (word-id binding + 1,134), Triton 2,516,630 (word-id binding + 2,562).
- **Recompute pin in `test_boolean_norms.py`.** Its `members_check` (cross-Call) finds exactly one recompute: on Triton, `DivFullRcp_v2`
  recomputes one gate of `DivFullScaleA_v3` (both read the divisor). That is allowed under Q_word v2 (#667). There are no `known.py`
  entries.
- **`targets.py` and `pins.json`.** These are the union. The one pin added is `RsqrtF32_v2{N=1,RSQRT=RsqrtApprox_v2}` = 1,134 ANDs
  (`--update-pins`).

## Checks on this head

- **vLLM lints** (`pytest integrations/vllm/tests/lint/`): all 43 pass on `a009c1cbc`. Your attention P9 fix is in.
- **circuit-check on my 12 targets** (`--as-call`): 10 ok and 2 fail.
  - The failures are `partition/gate-recomputed`, one gate each, on your Boolean-MUFU norm roots:
    - `RMSNormFusedCuda_v3{N=16,EPS=1e-05,RSQRT=RsqrtApprox_v2}`: gate 101216 recomputes 101115.
    - `RMSNormTriton_v2{...,SQRT=MufuSqrtFtz_v2,SCALEA=DivFullScaleA_v3,RCP=DivFullRcp_v2}`: gate 94385 recomputes 92898.
  - Each is a recompute across an opaque Boolean MUFU Call, which #667 allows. The same roots with the word-id MUFU pass, and so does
    `RsqrtF32_v2` with either RSQRT.
  - **Under the ruling these get no `known.py` entries. But `circuit-check --all` (and so `check`) exits 1 on them until circuit-check
    applies Q_word v2.** Either your roots wait for that or PR 2 cites #667 for them. That call is @circuits'.
- **Quick tests pass:** `test_boolean_norms.py`, `test_boolean_dense_norm.py` and `test_boolean_switch.py`; also `test_boolean_dense.py`,
  `test_derive.py`, `test_applicability.py` and `test_composition.py` (run on `8720cbec4`), and circuit-check's
  `test_every_registered_definition_is_checked`.
- **Slow tests pass:** Gemma-2's chain at H on `boolean_dense`'s rows with either RSQRT, `RsqrtF32_v2` and `NarrowF32ToBf16_v2` at H,
  and B1's norms on Boolean MUFU at N = 576.
- **The torch frontend's unversioned `AmpereBF16TcDot16` does not break on the merged tree.** Even with `verity.ml.boolean.gemm` imported,
  `ops["AmpereBF16TcDot16"]` is `AmpereBF16TcDot16_v2`, because bare names resolve only to word Definitions (`49e59afd1`). I dropped my
  stale comment about it (`a9d9825c3`).

## What the 80k-row evidence covers

- **The mean's 80k rows at H still hold:** `MeanTriton_v2` is unchanged.
- **The chain's 80k rows (`d95d51132` / `a4f011467`) were taken on my old copies of the eight.** On this head the chain at H is checked
  against `boolean_dense`'s rows with 43 rows, with each RSQRT binding.
- **5:21 AM PDT: 30k rows pass.** Groups 0–2 of `test_the_chain_is_gemmas_on_80k_rows` (`VERITY_VLLM_BOOLEAN_NORMS_FULL`) pass on
  `a009c1cbc`: 30k rows of Gemma-2's chain at H on `boolean_dense`'s rows and proofs' `RsqrtApprox_v2`, each with and without a
  residual. Groups 3–5 are running; groups 6–7 are not yet run.
