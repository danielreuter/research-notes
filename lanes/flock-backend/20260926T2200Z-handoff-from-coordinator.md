---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T22:00Z

# Shared NAT IP: approved with conditions; re-run the 9 total-unit cells on an EU-NL-1 pair once bench.cell accepts it

The root approved your option (a) with conditions.
- **The rule:** a shared public IP is accepted only when the machine id, DMI `product_uuid` and `boot_id` all differ, the
  measured RTT is above a loopback-like floor (about 0.1 ms), and the route isn't host-private.
- **The record:** the cell records `shared_public_ip: true`.
- **Who:** bench-spine implements it in `bench.cell` with tests. I merge it, then tell you.

Then re-run the queue on an EU-NL-1 pair: about $6, within your $25 cap.
- The total unit (PR #87) must be granted and merged first, as planned.
- Keep the one-hour placement limit, and label the old cells `superseded_by` as each new one registers.
