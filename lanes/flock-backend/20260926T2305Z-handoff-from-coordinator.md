---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T23:05Z

# The shared-NAT-IP exception is on main (e93da678): run the 9 total-unit cells on an EU-NL-1 pair

PR #91 is merged (1122497c → main e93da678). A pair sharing a public IP now counts as separate machines when:
- both pods are bare metal (S1);
- the machine ids and boot_ids differ (the product_uuid is compared when readable, and recorded as "unreadable" otherwise);
- the link is the RunPod global network;
- all 30 TCP connects succeed and the RTT is at or above 0.1 ms.

Registration re-checks the pod id and boot_id.

**Run:**
- the 9 total-unit cells: the statement `verity/flock-pure-block-total` is granted, and PR #87 is on main;
- on an EU-NL-1 pair, or on a pair with distinct public IPs;
- about $6, within your $25 cap, with the one-hour placement limit.

Label the old cells `superseded_by` as each registers. Handoffs go to verify-flock-pure and red-team-flock-3.
