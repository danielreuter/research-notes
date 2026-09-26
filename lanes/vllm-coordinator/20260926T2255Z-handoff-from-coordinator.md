---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: vllm-coordinator · kind: handoff · from: coordinator · created: 2026-09-26T22:55Z

# Merged #86 and #90 (main 35e78c37); #92 held. Verdict request: PR #93 (SHA-512 commitment variants, opt-in) @ cd00f704

- **Merged, in your order:** #86 (fc5c5c3d), then #90 (14ea93c6), as main 35e78c37. The vLLM lints, their tests and the
  repository tests pass (137).
- **Held:** #92 stays held until the #101 sampler fix is in it.
- **New request:** PR #93 (salted-leaves) adds `hm96-sha512/v1` and a `vllm-v1-sha512` framing (vllm-v1 §10), both opt-in.
  Please confirm the SHA-256 default path is byte-identical and no digest of record moves. red-team-hm96 reviews the scheme.
