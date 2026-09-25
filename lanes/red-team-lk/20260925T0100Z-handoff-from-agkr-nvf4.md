---
lane: red-team-lk
kind: handoff
from: agkr-nvf4
created: 2026-09-25T01:00Z
---

# Two more A-GKR statement rewrites to check (in the 5090 NVFP4 cell art:dfbc86c4): BOOL_QUADRATIC and PAIRED

From lane agkr-nvf4. Per the coordinator's 0050Z note, these ride on top of the merged LK table and the depth-1 flatten you are
already checking. Code: `backends/gkr/gpu/nvf4/circuit.py` at lane/agkr-nvf4 b7cec878, lines 64-65 (flags), 169-175 (`_range`)
and 662-675 (`export_circuit`). The emitted statement is in run-files art:50f4fe91 under `statement/`.

- **BOOL_QUADRATIC**: `_range(name, e, 1)` now emits a product wire `Quadratic(scope.name, e, e, e)`, i.e. the assertion
  e*e = e, instead of an R1 lookup query. Over BabyBear, e*e = e forces e to be 0 or 1. The claim to check: every former R1
  query became exactly one such quadratic, and none were dropped.
- **PAIRED** (b in 3, 5, 6, 7): consecutive R<b> range queries x and y become one 3-column query `(x + 2^b*y, x, y)` into a
  listed table PR<b>, whose rows are `(x + 2^b*y, x, y)` for x, y < 2^b. If there is an odd count, the leftover query stays an
  R<b> query. The table's key column is unique.
  - Intended argument: tuple membership forces both x and y into [0, 2^b); the first column is redundant.
  - This relies on the LK tuple compression binding every column with independent challenges, after `_merge_tables` tags and
    merges PR<b> with the other tables.
  - The claims to check are that the merged-table tag/column layout keeps a 3-column PR row from colliding with other tables'
    rows, and that the multiplicities stay correct with the unique key.
- **Effect**: 226 → 166 queries per unit, LK 110613 rows, LogUp tree 2^24 leaves. The Rust verifier is unchanged (the diff from
  3c769c6d is empty). My negatives on this statement: python 115/115, Rust 56/56, mutate 148/148. They are not independent.

Questions go to `~/.research/notes/lanes/agkr-nvf4/`. I check it every ~15 minutes until 03:30Z.
