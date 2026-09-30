---
id: 20260930T2022Z-handoff-from-network-accounting-utilization
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: network-accounting subcoordinator (bc-ecea50f6-c509-5918-b17a-d2148d57728f; @network-accounting)
---

# @old-accounting: two more network questions, for Daniel's priority 1 (shared infra on the two servers)

An addendum to `note:20260930T2008Z-handoff-from-network-accounting-network-state`. Same reply place and deadline:
`lanes/network-accounting/`, by 21:30Z, or a network section in your 21:00Z reply.

8. **Utilization failures, last 48 hours.** Which utilization failures did network work hit or cause on node 1 or node 2 (idle
   GPUs, a job stuck behind a lease, a check slot taken, a failed launch such as `r20260930-140951-8447`)? One line each, with a
   run id when there is one.
9. **Network workloads on the nodes.** Which network-warden jobs ran or were planned on the nodes: the #326 check
   (`r20260930-151146-adaf` on vy-nebius-2), the cold Lean export (`r20260930-141645-7405`), the deferred honest-trace run
   (per-token timestamps, one L40S, three modes, about 15 GPU-hours), a jitter (J) test. For each: which node, how long, how
   often, and whether it needs quiet or dedicated hardware. Timing measurements do, since a co-tenant or a frozen scope skews
   the timestamps.
