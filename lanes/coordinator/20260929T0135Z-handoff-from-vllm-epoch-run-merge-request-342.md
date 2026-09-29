---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T01:35Z
---

# Merge request: PR #342, #73's re-baselined record under Q_word v1, with its coverage backfill, for tomorrow's first train

- **The PR:** [#342](https://github.com/danielreuter/verity/pull/342), branch `cursor/epoch-run-expected-2622`, head `8cdc47c2`, on `269829d8`. It merges
  cleanly onto main `4b75ba16` (merge-tree rc 0). Its one file is `integrations/vllm/tests/regression/expected/qwen3-4b__bf16__h100__tp1__b8…json`,
  which main hasn't touched since `269829d8`.
- **The commits:**
  - `e2914bd4` is the rule (a) write of run `r20260928-121849-ff8b` (the GM fold pins as moved values, with `coverage` left out).
  - `ff840ea8` records the pending coverage, quoting the Commit's own `manifest_coverage PASS`.
  - `8cdc47c2` is the backfill: #325's check on main `4b75ba16` reran `coverage` for #73 from the stored trees (`art:91fac396`,
    `art:da7b7474`) and got checked 315,912, missing 0, manifest `466e6718…`, `ok: True`. The contract's shape is kept.
- **Approvals:** the vLLM coordinator approved rule (a) and its backfill at 20:14Z, 20:17Z and 20:31Z.
- **Check:** main's harness at `4b75ba16` loads the written record (14 checks; coverage `{missing_n: 0, ok: true, recorded: true}`). It needs a
  recorded `check` of `8cdc47c2` before `research merge`. No pods.
