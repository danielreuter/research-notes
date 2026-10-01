---
id: 20261001T0729Z-handoff-from-circuits-commit-tokens-coverage-v1-head
campaign: verity
lane: circuits-replay-keep-leaves
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-tokens (bc-aa52a6d5)
---

# @circuits-replay-keep-leaves: `cursor/coverage-v1-2622` is at `8185e277e`, with the Commit's token record merged over your slim keep (12:29 AM PDT)

- **The head:** `8185e277e`, a fast-forward of your `4764da87e` (no force). It merges the token-record change: PR branch
  `cursor/commit-tokens-record-8c79` (`348c28ee7`, `6106fa814`), ported as `79e7cce87` and `df0c02972`.
- **The merge was clean.** The one file we both changed is `integrations/vllm/verity_vllm/pipeline/row_config.py` (my module docstring,
  your additions); both are intact.
- **Tests on `8185e277e`:** `integrations/vllm` `tests/check`, `tests/lint` and `tests/pipeline` ran 1,216 tests: 0 failures, 39 skipped.
- **Please sync node 1's tree to `8185e277e`** when you next sync it. I have not touched node 1.
- **What changes on a run:**
  - A config run writes `commit/tokens_p<pair>.json` beside the Commit and links an early EOS stop to it.
  - A full row with a Match record needs both links only when the row committed `runner.sampler/sampled_token_ids`.
  - A full row that committed none records the token-record link as `not_applied`; its Match link alone decides, as before.
