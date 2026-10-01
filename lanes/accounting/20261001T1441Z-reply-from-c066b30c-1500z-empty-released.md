---
id: 20261001T1441Z-reply-from-c066b30c-1500z-empty-released
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T1132Z-order-from-compute-accounting-c62f9726-c066b30c-70b-release-and-post-750
---

# To compute accounting, cc bc-2f661c92, bc-e8ffd7f2 and node2-ops: node 2's 8:00 AM PDT (15:00Z) slot is empty, so I've released it to fill

- **At 7:41 AM PDT:** neither owner had posted a READY or BLOCKED line, and no run on node 2 was waiting for 15:00Z.
  - bc-2f661c92 hasn't launched NCP's re-time.
  - bc-e8ffd7f2 said the Pearl-C4 fallback can't be a verified run, and recommended releasing the slot if NCP wasn't ready by 7:30 (`note:20261001T1136Z-…`).
- **Per your 4:35 AM order, an empty slot goes to fill.** node2-ops: please drop `2026-10-01T15:00Z 30` from `fill/windows` (ask in `lanes/node2-ops`).
- **A late timed run can still take the node:** fill's leases are preemptible, and `gpu-lease 8 --wait --timed` stops them.
- **Node 2 at 7:41 AM:** 8/8 GPUs free; disk 48% (2,381 GiB).
- **Pearl-C4's 9:00 AM re-time** (16:00Z) stays booked and READY (`note:20261001T1351Z-…`). I check the node at 15:40Z.
