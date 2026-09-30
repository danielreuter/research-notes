---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
id: 20260930T0631Z-handoff-from-nebius-infra-steward-plan-agreed
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> root: the shared-infra model is agreed with POUS (06:24Z) and in force

**The plan (for Daniel):** `docs/shared-infra-plan.md`. Agreed with pous infra (bc-efe47341) at 06:24Z in
`lanes/nebius-infra/20260930T0624Z-reply-from-pous-infra-agreed.md`:
- **One branch:** `infra/nebius` holds the shared server code. Both sides push small tested commits to it, and it lands through
  the trains. Project branches stay on main.
- **Drift:** checked hourly against deployed hashes.
- **Lessons:** one append-only log, `lanes/nebius-infra/lessons.md`, 33 lessons so far.
- **Urgent pings:** PR #494, which never merges. POUS is subscribed; please subscribe.

**Found so far, all routed:**
- **Idle servers:** both were about 99% GPU-idle from boot to 06:25Z (node 1: 0.4% of 9.2 GPU-hours busy, 8.8% CPU).
- **Blocked cutover:** train checks take `gpu-lease` although they're CPU-only. That blocks M0's cutover, and after the cutover
  every check would fail. Sent to RC; checks get CPUs 128–191 without `gpu-lease`.
- **Conflicts:** #485 conflicts with #488 in `cancel.py`, and with `infra/nebius` in `gpu_lease.sh`. The resolutions are with RC.

Next I'm launching theory lanes where the workstreams are theory-bound.
