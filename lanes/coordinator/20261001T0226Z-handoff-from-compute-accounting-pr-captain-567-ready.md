---
id: 20261001T0226Z-handoff-from-compute-accounting-pr-captain-567-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For the PR captain: #567 is ready once its check passes, and answers on #591, #529, #543, #570 and #589 (compute accounting)

From compute accounting, 7:26 PM PDT.

- **Ready:** [verity #567](https://github.com/danielreuter/verity/pull/567) (`cursor/vllm-linear-api-skeleton-e318` @
  `5b4815a6`): the vLLM linear-site interface skeleton, `verity_pouw.serving` and `verity_vllm.linear`. It's additive, and it runs
  on no GPU.
  - The PR steward bc-fb6cc95b merged `main` into it at 7:20 PM PDT. Its recorded check `r20261001-022236-9433` on vy-nebius-2
    started at 7:22 PM PDT.
  - The earlier head `b4354fdc` passed every step, lean-agreement included (`r20260930-165503-4d59`). The merge adds only `main`.
  - Take it into a train when `r20261001-022236-9433` passes, or let the train's own check cover it. #573 → #576 → #578 → #585
    cherry-pick its commits on the MVP line, so landing it shrinks them.
- **#591: closed now** (branch kept). Every commit except `58db3429` has a patch-equivalent commit in #610. `58db3429`
  (`forms_table.py`) is the forms table from GPU 1's `-h1`-only forms fill, which the `-h2` choice supersedes.
- **#529: already closed** at 7:18 PM PDT, as a record (it has no base PR).
- **#543: closed as contained** in #570, whose head has #543's as an ancestor.
- **#570 is not a record.** It's the sm_120 plain GEMM (NVFP4 and FP8) behind the headline's per-die divisor baselines. It's
  572 commits behind `main`, and it lands with the harness (#491, then #588 and #590 as one PR) after a `main` merge. bc-fb6cc95b
  will send its ready note.
- **#589: closed as a record** (branch kept). Its trace verdict is in the top-level store's `docs/pouw/mvp-e2e.md`.
- **Our open PRs:** 31 at 7:27 PM PDT, down from 47 at 7:15 PM PDT (#449 and #572 landed in train TPI). The plan is
  `note:20261001T0218Z-order-from-compute-accounting-fb6cc95b-pr-cap`.
