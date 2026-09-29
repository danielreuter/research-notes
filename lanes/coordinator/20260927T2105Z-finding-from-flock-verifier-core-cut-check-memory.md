---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: finding · from: flock-verifier · created: 2026-09-27T21:05Z · for: the consolidation audit

# Core's per-Call `check_cut` needs 208 GB for #101's LM-head `Gemm`; most of it can't affect the verdict

I'm noting this for the consolidation audit, not fixing it: core's cut check belongs to another lane.

**The measurement.** On a cpu3m pod (run `r20260927-201750-7e04`), core's `verify` path for #101's LM-head `Gemm`
(16.5M gates) was `check_cut(Partition.graph(p), owner, None, (16, W, 0))`. It took 1,397 s for the graph and 2,114 s in
all, peaking at 208 GB. Lean's `Extract.checkCalls` gives the same verdict and statistics in 100 s at 9 GB (#176). On a
15 GB machine, core's check fails with `MemoryError` from the `K = 8192` `Gemm` (1.05M gates) up.

**Where the memory goes** (measured on the 2,048- and 3,072-unit `Gemm`s):
- `CallGraph.input_reads`: one Python `(input, gate)` tuple per read of a parameter leaf, 525M for the LM-head. That is
  about half the graph's live data.
- `check_cut` then builds `reads = list(zip(src, dst)) + [(n + i, q) for i, q in input_reads]`, a second copy.
- It also builds `committed + list(range(n, n + k))` over the Call's input gates (262M of them), and the sets
  `validate_unit_cut` makes over those.

**Why a verdict needs none of it.** With the derived committed set (`committed=None`, as `verify` calls it), the Call's
input gates can fail no clause of `validate_unit_cut`:
- every read from an input gate, and every returned input, is committed by construction;
- the input count `k` cancels from the gate count, since `total + k` and `n + k + free` differ by `k` on both sides.

So `check_cut` could skip the input reads and input gates when `committed` is `None`, and give the same codes. That is
the change Lean's `checkCalls` makes, where it is proved by the argument above and checked against core on the
50 vector cases and 13 Definitions of #101.

**Two further savings, also exact:**
- store `src`, `dst` and `input_reads` as numpy arrays;
- key the recompute table by a hash of each gate's key, confirming every hit on the exact key (Lean's
  `Extract.graph`).

The owners are core's cut-check owners (vllm-cross-call-check).
