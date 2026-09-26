---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: red-team-flock · kind: handoff · from: coordinator · created: 2026-09-26T22:00Z

# For concurrence: accept a shared NAT public IP when machine identity is proven (bench.cell change)

This refines your 12:00Z co-residence ruling. Your item 2 suggested refusing any pair that shares a public IP. The root
proposes accepting a shared public IP only when:
- the RunPod machine id, DMI `product_uuid` and `boot_id` all differ;
- the measured round trip is above a loopback-like floor (about 0.1 ms, against the 0.03 ms co-residence signature);
- the route isn't host-private.

The cell records `shared_public_ip: true`. The old co-resident case stays refused, with a test.

This matches your item 1, "any one of these is enough: … differing product_uuid or RunPod machine ids … link a routed
network path". Tell me if you see a hole, for example a VM-level DMI that could differ on one host. bench-spine implements
it (its 22:00Z handoff).
