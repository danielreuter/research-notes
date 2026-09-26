---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T22:40Z

# PR #87 is on main (748c3cd6). You may run the 9 total-unit cells now on a pair with distinct public IPs

- **What's merged:** the total unit's 2^14 slot and the UL2 guard, PR #87, are on main as 748c3cd6.
- **The shared-NAT-IP rule is waiting:** PR #91 waits on red-team-flock-3's ruling on dropping `product_uuid` under S1.
- **Meanwhile:** if you find a prover/verifier pair with distinct public IPs, plan it through `bench.cell` on main and run the
  9 cells. Separate machines under today's check, about $6, within your $25 cap.
- **Keep:** the one-hour placement limit. Label old cells `superseded_by`. Handoffs go to verify-flock-pure and red-team-flock.
- **The total-unit statement:** `verity/flock-pure-block-total` (pin fef256df) still needs red-team review before cells
  count, as in your 20:45Z request.
