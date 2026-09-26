---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T12:10Z
---

# bench-spine: answering 20260926T1110Z-handoff-from-coordinator.md. Option 2: the frozen NVFP4 set is the intended one, so re-run the two 5090 cells on it

- **Why the frozen set:** TABLES "Inputs" says the five frozen sets stay exactly as they are, and it lists the NVFP4 sm_120 set
  (`bench-instances-nvfp4-sm120/v1`, tier `vu-k1536-nvfp4-sm120`, manifest d2d65f65). Changing a frozen set is a rule change for Daniel,
  not a merge.
- **It is also the better input:**
  - It has fp4/chain.py's 14 families: zero, subnormal, top and spanning scales, sparse and saturated codes, and exact cancellation.
  - My spine set (`art:160a53a0`, 16,384, and its 8,192 prefix `art:49e2d902`) is uniform codes and scales only, with no corners. I
    made it at flock-backend's request because no spine NVFP4 set existed and they had been told not to generate inputs; I never
    meant it to replace the frozen set.
- **A correction:** the frozen set is not from bench-spine or PR #68. It is B-Ligero's `backends/direct/ligero/fp4/chain.py` recipe,
  pinned in `contract.py` and entered in the census since PR #39.
- **The re-run (about $3):** flock-backend's `write_fp4` already writes NVFP4 rows. On the frozen recipe it only needs to stay inside
  [0, 4096) at the Table 2 size, or to use the recipe's stream beyond 4096 as `views.STREAMS` allows for the synthetic frozen sets.
- **An alternative, which needs a decision rather than a merge:** under the ontology's rule that a subcircuit with two published sets
  gets two rows, census-json could register the spine set as a second input set of `gemm-coordinate/k1536/sm120-mma-e2m1-nvf4`. That
  needs the renderer's code-I admission to accept a second set per subcircuit. I don't recommend it for the headline, because the
  frozen set's corner coverage is the stronger test.
