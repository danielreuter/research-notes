---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:40Z · re: `lanes/vllm-epoch-run/20260928T1947Z-GO-from-vllm-coordinator-101-try5-pr321.md`

# #101's fifth try, on #321: G3 now passes; G4 fails by 32 instances. Deferred.

- **Run** `r20260928-194951-f7ed` on `703ae80f` (tree `b47baad5`). The Build passed at 20:30Z: digest `11e8da5d…` (the same as try 4), manifest
  `1ea8e220…`, 8,067 identities.
- **Both of your expectations hold:**
  - The Match was given `--program-dir …/build_request`.
  - `fold_summary.json` has `sampler_construction: greedy-check-per-stage`, and `by_spec` has `GumbelTopPTokenSelect_v1{V=128256}` ×32
    (with `by_pattern.sample.gumbel_topp_select` at 448).
- **The Match** failed at 20:33Z. The verdict passed, `tokens_equal` was true and the fold passed, but the global Match failed on **G4** alone.
  **G3** (`subcircuits_x09`) now passes; it failed on try 4.
  - G4 is `identity_map`: "(request, local step, local index) <-> global node is a bijection over the attributed fold". It has one
    problem: `r0: address map declares 46686 instances for the request, the component has 46654`. The mapped, attributed and distinct
    counts are all 46654, with `weight_only_shared` 0. The gap, 46686 − 46654, is 32: the number of top-p selects the fold binds.
- **What happened next:** a GREEN row with a failed Match isn't committed, so #101 is deferred. The Build is stored as `art:0e6911da…` and
  the records as `art:55029fe0…`, both preserved. The pod was terminated at 20:39Z. This try spent $0.91, and #101's five tries $3.31 in total.
- **The digest line** says the same. The record stays the old one.
