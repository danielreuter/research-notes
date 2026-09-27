---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T13:25Z

# After the morning report (not tonight, no pods): a totality fix in the top-p split reference, like #103

- **What:** the lowering lane found a case where the sampler's `topp_split` reference is not total. It raises on rare rows that no
  served test row reaches.
- **Detail:** it is private. Read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/private/flock-ir-lowering-topp-split-half-divergence.md`,
  and don't copy it into `internal/` or your lane folder; see lane contract 2.2, §5b.
- **Needed:**
  - defined behaviour on every input, matching the kernel where the kernel is defined. Say how the chosen rule relates to what the
    split kernels do on such a row;
  - no change on the rows that don't hit the case: `TopPMaskWordx128256_v1`'s digest and #101's Program and manifest unchanged, as in
    #103;
  - a test on a **constructed** row that hits the case. Put the test itself in the PR, but keep the construction's explanation neutral
    and don't restate the private note;
  - the one `sampling.topp_keep` statement stays the single place the semantics live, and `ir_sampling` follows it;
  - lints and a test diff. CPU only, $0.
- Merge-ready handoff to `internal/lanes/vllm-coordinator/`, carrying the verdict and a pointer only.
