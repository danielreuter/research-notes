---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (merge request, TOP vLLM priority) · from: vllm-coordinator · created: 2026-09-30T18:56Z

# [#594](https://github.com/danielreuter/verity/pull/594) @ `6a7ff6526742209f3cf95be6f259cf6665b026e9`: the bounded-staging warm-up keeps the requests' sampling fields. GRANTED 18:55Z. Next vLLM train, please

- **The bug it fixes:** the fail-closed +256 B staging failure that holds **130 stochastic deployments**. The warm-up dropped the per-request `seed`, so its learned plans lacked the seed tail every seeded Commit step stages.
- **Scope:** `engine/vllm_adapter.py` (warm-up requests only) plus one test. `integrations/vllm/` only, 2 files, clean on main `d079ac2c`. The lints and the new and adapter tests pass.
- **What doesn't change:** what vLLM runs in the committed run, the committed bytes, and any record digest. Proved: SmolLM2-360M Gumbel's run root is identical before and after.
