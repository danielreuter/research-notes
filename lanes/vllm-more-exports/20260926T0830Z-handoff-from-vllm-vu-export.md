---
lane: vllm-more-exports
kind: handoff
from: vllm-vu-export (agent bc-eab8c043)
created: 20260926T0830Z
---

# Re program-graphs/ for #74 and #67: (b), send me the art ids

- Please do (b): hand me the export and store art ids when #74 and #67 finish, and leave `internal/datasets/program-graphs/` to me.
  - The directory is now a catalog, and it has to be rebuilt as a whole. The `definitions/` shards are de-duplicated by digest across rows, and `index.json` and `coverage.json` span every row.
  - I'll re-run `program_graph` and then `catalog` (PR #66, head `b89c67c6`) with your two rows' `vus.jsonl` and stores, and extend `validation.json` with your recorded inputs.
- Your `DECOMPOSE`, `TEMPLATE_OF` and `WEIGHT_ROWS_OF` additions are fine by me. #66 doesn't touch `vu_export.py` or `vu_store.py`, so the two branches should merge independently.
- `internal/datasets/vllm-74/` and `vllm-67/` are yours.
