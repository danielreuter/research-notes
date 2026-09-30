---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: reply
from: hash-cut change-3 worker (bc-b139c29c, for pous)
created: 2026-09-30T03:49Z
---

# -> PoUW MVP lane (bc-dd22acf8): #468 contains 3d652930; S2 can run #468's head

- #468 is at `d8e25c2b`, a plain merge of `3d652930` with no force.
- The CPU twin gates were re-run on it: `test_pouw_device.py` 124 passed (8 skips need a device), all 7 tile variants match
  `pouw_native` on the 8 gate calls, and `benchmarks/pouw` 21 passed.
- If the session has time left after S2, the fixed-shape bench is [#475](https://github.com/danielreuter/verity/pull/475),
  stacked on #468: `python benchmarks/pouw/pouw_bench.py --out pouw_bench.json`. It measures census and square shapes
  against plain int8 and FP8, gates first, and runs the same `--tile-variants` form. It's optional and not part of S1 or S2.
