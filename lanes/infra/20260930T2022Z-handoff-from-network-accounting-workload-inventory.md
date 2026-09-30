---
id: 20260930T2022Z-handoff-from-network-accounting-workload-inventory
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: network-accounting subcoordinator (bc-ecea50f6-c509-5918-b17a-d2148d57728f; @network-accounting)
---

# @network-accounting's workloads: one check now, one timed GPU run later, everything else runs on the agent's VM

Scope: the network warden (`protocols/network_warden`, its Lean package `NetTiming`) and network resource guarantees. Sources:
#326's merge request (`note:20260930T1535Z-handoff-from-network-warden-326-merge-request`) and the old network-timing agent's
record. @old-accounting's list of utilization failures from the last 48 hours comes later
(`note:20260930T2022Z-handoff-from-network-accounting-utilization`).

| Workload | Node, resources | How long | How often | Isolation |
|---|---|---|---|---|
| **#326's re-test**: one full `check` of #326 merged with current `main`. It touches the root `pyproject.toml` and `uv.lock`, so every suite reruns. | CPU, a check slot. The last one ran on vy-nebius-2 (`r20260930-151146-adaf`). | about 12 min (724 s last time) | once, to land it; again only if `main` moves before the merge | none |
| **The warden's Lean build and audit** (`NetTiming`, Mathlib cache) | CPU, inside `check`. The cold dependency export ran once (`r20260930-141645-7405`). | minutes, warm | per Lean change; none planned | none |
| **The warden's suite** (66 pure-Python tests) and **calibration** (`network-warden-calibrate` over trace JSON) | the agent's VM | under a second to a minute | per change | none. The tests don't read the clock. |
| **The honest-trace run** (deferred, not scheduled): vLLM per-token network timestamps in three modes, to calibrate the honest miss rate | 1 GPU (it was sized on an L40S; the same GPU class as the deployment it models) plus its host's NIC | about 15 GPU-hours, in about 5 h chunks per mode | once, then per recalibration | **quiet or dedicated:** no co-tenant on that GPU or NIC, and no freeze or SIGSTOP mid-run, since a pause or a neighbour skews the timestamps. It needs a `timed` / `quiet=True` lease, not guest fill. |
| **A jitter (J) test** (future): the warden's emission jitter on real hardware | 1 host plus its NIC | under 1 h | once per hardware class | **quiet or dedicated,** as for the trace run |

**Asks:**
1. Where does #326's re-test go today? Is it the next merge train's check, a `check.py --record --on <pod>` in a node-2 check
   slot, or a Verity guest job on node 2's pool (`note:20260930T2015Z-reply-from-node2-ops-verity-pool-live`)? I'll move it
   onto the central queue as soon as the queue takes jobs.
2. The honest-trace run waits for Daniel's go and for a quiet slot. When the queue has a `timed` class for guests, tell me its
   lead time.
