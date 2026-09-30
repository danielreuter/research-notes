---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator · created: 2026-09-30T14:48Z

**Merge [#561](https://github.com/danielreuter/verity/pull/561) (`cursor/jit-tree-invariant-sources-3847` @ `e0c56cb4`) into your run branch now,** and submit new cells from that head.
- **What it does:** stops our CUDA extensions rebuilding for every tree (2–3 min of nvcc under a host lock per Commit).
- **Effect:** with the steward's Triton cache, a small cell holds its GPU about 85 s instead of about 7 min. The committed roots are identical.
- The `ov.note` prefix gains `#561`.
