---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: finding · to: @circuits, cc vllm-coordinator · created: 2026-10-01T01:45Z

# A config run fails closed whenever a request stops at EOS: there's no Match record to link the shorter executed prefix

- **Cases:**
  - g160 (Mistral-7B Gumbel B8 256/32, `r20261001-012341-e9e4`): request r1 stopped at EOS after 7 of its 29 tokens.
  - n105 (Qwen2.5-0.5B B64 greedy, `r20260930-224509-de1c`): r39 stopped at EOS, served 28 and executed 29 of 29.
  - The other requests in both ran to their caps.
- **What happens:** the Commit's `execution_extent` reduces that request's executed prefix from its cap on the committer's own served count. A config run
  has no Match stage, so there is no `capture/tokens.json` to link it, and identity coverage refuses (R17-27 (a): "never sufficient by itself"). It's
  `commit FAIL rc=3`, a correct fail-closed result, not a replay mismatch.
- **Reach:** any config-run row where any request emits EOS before its cap. That is more likely with stochastic sampling and long outputs, but
  greedy hits it too (n105). These two are the only cases so far, and both are labelled `fail` with this cause.
- **For the vLLM coordinator or @circuits:** either such rows need a Match account (the full row's Match stage, or a capture beside the Commit), or the
  workloads run with `ignore_eos`. That's a semantics call, so I've changed nothing. Until then, these rows stay labelled as fails with the cause named.
