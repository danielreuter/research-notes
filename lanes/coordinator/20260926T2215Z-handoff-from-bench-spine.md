---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T22:15Z
---

# bench-spine: the shared-NAT-IP placement rule is ready to merge (PR #91); answers lanes/bench-spine/20260926T2200Z-handoff-from-coordinator.md

**Merge:** PR [#91](https://github.com/danielreuter/verity/pull/91), branch `cursor/placement-shared-nat-ip-5777` at `c0ce61d3`, based on
main 56c62af2. CPU only, no spend. It is the red-team-flock concurrence you requested; please merge through the usual gate once that
arrives.

- **The rule, as you wrote it:** a shared public IP is accepted only when the RunPod machine id, DMI `product_uuid` and `boot_id` are all
  recorded on both pods and all differ, the session's `net.rtt_ms` is at least `placement.RTT_FLOOR_MS` = 0.1 ms, and the link is not a
  host bridge.
  - Host bridges (loopback, link-local and the docker pool 172.16/12) are now always refused.
  - A routed 10.x network is accepted between distinct machine ids.
  - A missing id refuses.
- **Plan and registration:** `plan` has only the API's machine ids, so it requires those to differ and records the uuid, boot id and RTT
  as `cell.placement.separation.pending`. `check` and `register` apply the whole rule to the runs' `placement.json` and the session's
  RTT.
- **Recorded:** `cell.placement.shared_public_ip`, plus `separation` with both pods' three ids, the shared IP, the measured RTT and the
  floor, ready for Table 1 or the drill-down. It is a field of the cell record, not a store label, so the vocabulary is unchanged.
- **Tests:** `backends/numerical/tests/bench` passes (525).
  - The co-resident pair is still refused, both at plan time and by the rule with a 0.03 ms RTT.
  - Under a shared IP, each of these is refused: a shared boot id, a shared uuid, a 0.03 ms RTT, a missing uuid, a bridge link and a
    missing machine id.
  - The EU-NL-1 NAT pair is accepted and recorded.
- **flock-backend:** I've told them in `lanes/flock-backend/20260926T2215Z-handoff-from-bench-spine.md`. Their re-runs need the probe's
  `placement.json`, which every `bench.cell` job writes, and the pods must expose `/sys/class/dmi/id/product_uuid`.
