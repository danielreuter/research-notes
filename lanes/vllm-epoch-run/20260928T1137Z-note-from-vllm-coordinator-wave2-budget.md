---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (NOT GO) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T11:37Z · supersedes the #74/#39 lines of `20260928T1135Z-note-from-vllm-coordinator-wave2.md`

# Wave 2: #74 is funded, #39 and #57 are deferred

**#74 is funded** (root's ruling). It's a 2× H100 on secure cloud, cap $49, 3 pairs, run eager.
- It launches only on a separate GO from me, once S1b (#253) is on main, and within its latest start.
- The committed-spend-plus-cap rule within $250 still applies.
- Also refuse the launch if it would take the RunPod balance below the $25 guard floor. That means balance less the committed caps of running rows, less about $7.55/h for the sweep lane until 18:00Z.

**#39:** deferred to the follow-up epoch, with its old record kept. It's blocked on #244 and unfunded.

**#57:** deferred to the follow-up epoch, with its old record kept (16.4 h of host time).
