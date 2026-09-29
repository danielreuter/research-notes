---
cursor:
  subagentId: "bc-d11231d9-cb4b-5d32-9f0e-5dd3c6d56e6f"
lane: coordinator
kind: note
from: consolidation (bc-e373566b)
to: constants (bc-613ddf45)
created: 2026-09-28T06:15Z
---

# The MUFU tables are moving to core: `load_tables.py`'s path stops existing when the move lands

Branch `cursor/mufu-prims-to-core-ac68` (stacked on #223's branch `cursor/silicon-prims-to-core-ac68`, not yet a PR) moves
the eight MUFU / `div.full` primitives and their measured tables from the vLLM integration into core `verity.ml.mufu`.
No table, pin or digest changes; only the files' location does.

- **Where the files go:** `packages/verity/src/verity/ml/tables/mufu_{ex2,rcp,rsq,sqrt}_delta_int8.xz` (the same bytes;
  `git` records them as 100% renames) and `mufu_tanh_sm89.{json,xzblocks}` (from `registry/quarantine/dense/tables/`).
  The `W11-*`, `W11C-*` and `W11R-*` directories under `integrations/vllm/verity_vllm/program/kernels/tables/` are gone.
  Their other copies (rcp in W11 and W11R, sqrt in W11R) were byte-identical duplicates and are deleted.
- **What breaks for you:** `internal/compile-time-constants/scripts/load_tables.py` reads
  `integrations/vllm/verity_vllm/program/kernels/tables/<W11 dir>/mufu_<name>_delta_int8.xz`. After the move, point `K` at
  `packages/verity/src/verity/ml/tables` and drop the per-table directory. The file names are unchanged.
- **Simpler option:** `verity.ml.mufu.table(name)` (`name` in ex2 / rcp / rsq / sqrt, or a table's SHA-512) returns the
  decoded words as a read-only `uint32` array. It raises `ValueError` unless the words hash to
  `verity.ml.library.table(name).sha512`, and their SHA-256 is the same pin your script checks.
- **Unchanged:** `verity.ml.library`'s entries (the file is left alone, since #201, #195 and #194 touch it),
  `ir_lower.write_tables`, the Lean archive keys and C-Flock's SHA-256 pins.
