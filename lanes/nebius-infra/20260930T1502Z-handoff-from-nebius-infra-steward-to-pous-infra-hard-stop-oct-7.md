---
id: 20260930T1502Z-handoff-from-nebius-infra-steward-to-pous-infra-hard-stop-oct-7
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for POUS infra (bc-efe47341)
---

# Both servers' hard stop is now 2026-10-07T15:00:00Z (Daniel, 7:54 AM PT); vy-nebius-2 is set and verified

Supersedes the 2026-10-02T04:57:26Z stop in `20260930T0540Z-note-to-pous-vy-nebius-2-access.md`.

- **vy-nebius-2, 15:00Z:**
  - `/etc/research/deadline` reads `1791385200 2026-10-07T15:00:00Z daniel-2026-09-30T1454Z`.
  - The lease is extended to its cap, **2026-10-07T14:55:00Z** (clamped-to-deadline). A renewal of 99,999,999 s stays at that
    cap.
  - `vy-deadline.timer` and `vy-lease.service` are active, and the running `lease.sh loop` reads the new cap every tick.
  - The VM stops itself at 14:55:00Z Oct 7, 5 min before the deadline, whatever the lease says.
- **vy-nebius-1** is the same.
- **Nothing else changed:** no Nebius resources, IAM or spend alerts (about $800/day and $24k/month still cover ~$710/day).
- **For your docs:** anything on node 2 that plans to the old stop (`server.md`, `status.md`, fill schedules) can plan to
  2026-10-07T14:55Z.
- **One oddity in node 2's `lease.log`:** a line dated `2026-10-03T05:32:24Z … TERMINATED computeinstance-e05v9sztsjcjsw4hm2`.
  It looks like a fixed-clock test wrote to the real log (the leak #504 isolates). The VM is up and its lease is intact.
