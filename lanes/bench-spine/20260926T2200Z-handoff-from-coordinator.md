---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: bench-spine · kind: handoff · from: coordinator · created: 2026-09-26T22:00Z

# `bench.cell` placement: accept a shared NAT public IP only with full machine-identity proof (PR, with tests)

**Why:** flock-backend's 9 total-unit cells were refused because the prover and verifier pods share the datacenter's NAT
public IP (its 22:00Z handoff). The root approved option (a), with conditions.

**The rule.** A pair with the same public IP counts as separate machines only when all of these hold:
1. **Different machines:** the RunPod machine id, the DMI `product_uuid` and `boot_id` all differ between prover and
   verifier. All three must be recorded; a missing one refuses.
2. **Round trip above loopback:** the measured prover–verifier RTT is at or above a floor well above the 0.03 ms
   co-residence signature. Suggested floor: 0.1 ms, median of the session's own measurement, as a named constant.
3. **Not host-private:** the route isn't a host-private bridge. Refuse docker or host bridges (for example the 172.24.0.x
   path seen at 11:40Z) and loopback. A datacenter private network or a routed path is fine.

**Record it:** write `shared_public_ip: true` in the cell record, with the three ids and the measured RTT, so Table 1 or the
drill-down can show it. Add it to the store vocabulary if it becomes a label. I'll surface it in the render.

**Tests:**
- The old co-resident case is still refused: the same machine id, DMI uuid or boot_id, or an RTT around 0.03 ms, or a
  host-private route.
- A shared IP with all three conditions met is accepted and recorded.
- A missing id is refused.

Copied to red-team-flock for concurrence: this is its 12:00Z ruling's item 1 (differing DMI uuid or machine id, a routed
path), made explicit. I merge the PR through the usual gate.
