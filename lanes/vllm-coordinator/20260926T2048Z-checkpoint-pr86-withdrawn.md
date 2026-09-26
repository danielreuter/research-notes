---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# 20:48Z

- PR #86 approval WITHDRAWN (the router recomputed the softmax per unit: 18,144 gates per token, a no-recompute violation). vu-export replaces it with a committed-softmax router. Re-review when updated.
- The review gate now requires the partition checker's recompute check = 0 (added to vllm-cloud-common.md).
