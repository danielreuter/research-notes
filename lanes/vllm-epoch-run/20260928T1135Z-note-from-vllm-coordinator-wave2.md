---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (NOT GO) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T11:35Z

# Wave 2 now

- **#57:** deferred to the follow-up epoch, with its old record kept. S1b's host evaluation is about 16.4 h per Commit.
- **#74:** runs once S1b (#253) is on main. That's a separate GO. Add about 25 min of host time per Commit, and run it eager.
- **#39:** only if #244 (`GemmBias_v1`) reaches main in time. It isn't there yet.
