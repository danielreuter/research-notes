---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-30T20:20Z
---

# Merge request: #597 at `61aff052`, one docstring line; small, fits any train

- **PR:** [#597](https://github.com/danielreuter/verity/pull/597), branch `cursor/mufu-table-path-docstring-ac68`, head `61aff052504c36b1bd1e00f45f1771abfa12f6cc`, from `main` `73eee493`.
- **Change:** `integrations/vllm/tests/acquire/fa2_attn_oracle.py`'s docstring names `verity.ml.mufu.TABLE_DIR` in place of the table directory #250 removed. It's #250's leftover, deferred because #228 edited the lines around it.
- **Tests:** `integrations/vllm/tests/lint` passes.
- **Grant:** `vllm-coordinator` only (`Rules.needs`), requested in `lanes/vllm-coordinator/20260930T2020Z-handoff-from-consolidation-597-grant.md`.
- **#228 and #250** are both on `main` (TCN at 19:14Z, TCP at 20:16Z). Thanks for running them.
