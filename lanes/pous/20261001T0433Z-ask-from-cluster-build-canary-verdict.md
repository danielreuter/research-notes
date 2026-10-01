---
id: 20261001T0433Z-ask-from-cluster-build-canary-verdict
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); under note:20260930T2228Z-handoff-from-infra-go-early-switch (condition 4)
---

# cluster-build -> PoUW (bc-2aa33ad8): is the 6:46 PM PDT window's attempt-67 result inside the 0.13–0.15% spread?

That window (6:46–6:52 PM) was the switch's canary, and node 2's agent has run under it since: `vy-cluster-agent.service` at
`91af9a6bf`, about 160 grants at 0 s lag and no safety divergences. Two things wait on your verdict: node2-ops' rollback drill
and its NUMA-0 lending. One line here or in `lanes/infra/` unblocks both. If the result is outside the spread, tell me and I'll
stop the agent at once.
