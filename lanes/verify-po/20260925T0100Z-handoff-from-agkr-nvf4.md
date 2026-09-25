---
lane: verify-po
kind: handoff
from: agkr-nvf4
created: 2026-09-25T01:00Z
---

# A-GKR RTX 5090 NVFP4 (fp4-nvf4) Table 2 cell, new best: verify art:dfbc86c4. NEW statement (BOOL_QUADRATIC + PAIRED), so hold the label per coordinator 0050Z

From lane agkr-nvf4, 01:00Z. This supersedes the 00:05Z handoff (art:49757870, 0.1905 s). The **statement changed** at b7cec878.
On top of the merged LK table and the depth-1 flatten that were already in 49757870, it adds two rewrites:
- **BOOL_QUADRATIC**: each 1-bit range check is now a `b*b = b` product wire (a `Quadratic` gate) instead of an R1 lookup query.
- **PAIRED** (b in 3, 5, 6, 7): two R<b> queries x and y become one query `(x + 2^b*y, x, y)` into a new listed table PR<b>,
  with rows `(x + y*2^b, x, y)` for all x, y < 2^b.

Result: 226 → 166 queries per unit, LK 110613 rows, 700 wires, depth 1, and the LogUp tree drops from 2^25 to 2^24 leaves.
Under the coordinator's 0050Z rule this gets a verdict, and the `verified=accepted` label is **held** until red-team-lk passes.
Please also pass BOOL_QUADRATIC and PAIRED to red-team-lk. The code is in `gpu/nvf4/circuit.py` (`_range` and `export_circuit`)
at lane/agkr-nvf4 b7cec878.

**Result**
- bench-result/v1 `art:dfbc86c4434000c61d3d6b991148c8e8e8e914dbbd6ef27093d0d4f47fcd6fe7`: attempt r20260925-004238-a4e2,
  PRESERVED, validation passed, contract_problems none, source lane/agkr-nvf4 @ b7cec878, clean.
- Setup: NVIDIA GeForce RTX 5090, fp4-nvf4, frozen NVFP4 set (`bench-instances-nvfp4-sm120/v1`, `vu-k1536-nvfp4-sm120`, seed 20260922),
  K=1536, B=4096, NON_ZK_PROOF_DIAGNOSTIC.
- Soundness 2^-130.19 (target 2^-128). t.total median 0.1604 s over 5 reps (0.164 / 0.162 / 0.160 / 0.160 / 0.157).
- run-files/v1 `art:50f4fe91635eb7216786ead66759ab90fdb6c3197258d957d0a7698f31e93bd8`: `proofs/rep{0..4}.bin` (9469288 B each,
  all sha256 `ebe7c545705c7e430571…`) plus `statement/`.

**Verifier**: `git diff 3c769c6d b7cec878 -- backends/gkr/verifier` is empty, and so is the diff to the current tip 79f00fd3.

**Command** (`DIR` = `research data fetch art:50f4fe91 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 673, msgs 1589, bytes_read 9469288, ligero_rows 11672,
committed_elements 47804437.

**Negatives** (mine, not independent), run on this n24 statement: python 115/115, Rust 56/56, mutate 148/148.
