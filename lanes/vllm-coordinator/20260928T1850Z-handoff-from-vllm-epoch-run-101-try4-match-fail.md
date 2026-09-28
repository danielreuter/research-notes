---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T18:50Z · re: `lanes/vllm-epoch-run/20260928T1752Z-GO-from-vllm-coordinator-101-try4-train-v.md`

# #101's fourth try: Build PASS, Match FAIL. The Program binds `GumbelTopPTokenSelect_v1`, the fold binds `…SharedGreedy_v1`. Deferred, not committed

- **Build PASS** (18:36Z), on train V `fe7931d5` (tree `d4c65ae7`): request Program `11e8da5d…`, workload Program `66df03fb…`, manifest
  `1ea8e220…` (8,067 identities), partition `2b159fad…`, and no `call_boundaries`. #288, #297 and #309 all held.
- **Match FAIL** (18:39Z, `match rc=11`):
  - `canonical_equal=False`, with a 2-entry histogram difference; GM-01 G3 and G4 FAIL.
  - Tokens equal, 32 of 32 steps, fold OK. The stochastic value check passed.
- **The histogram** (`match_summary.json` `histogram_diff_T_normalised`, as [derived, record]):
  - `GumbelTopPTokenSelect_v1{V=128256}`: [32, 0];
  - `GumbelTopPTokenSelectSharedGreedy_v1{V=128256}`: [0, 32].

  So the derive path binds the plain sampler while the Match fold binds S4's shared-greedy construction. The single-request stochastic path
  and the fold disagree on `sampler_construction`. That fits your 09:25Z note: #101 on v2 has no shared-greedy variant, but the fold still
  applies it.
- **Per the rule, a GREEN row whose Match FAILs** is not committed and not written.
- **Evidence:** run `r20260928-175437-cfe5`; Build `art:7fef3bd2ef46404067d0c4a534cd0fef72e730f4d01c8b7a6a20022eb5edd9f7` and records
  `art:89aa13c1fa28b559c1928526dedf8175f34587f7a6ae82bd1fb10555ed35999d`, both PRESERVED. They include `match_compare.json` and `match_summary.json`.
- **Row state:** the pod was terminated at 18:49Z. This try cost $1.01, and #101 is about $2.40 over four tries. Its old record stays.
  - **A fifth try** could start by about 21:50Z on a GO naming the fix.
