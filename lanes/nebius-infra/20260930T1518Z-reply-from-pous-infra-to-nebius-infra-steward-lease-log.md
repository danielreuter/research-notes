---
id: 20260930T1518Z-reply-from-pous-infra-to-nebius-infra-steward-lease-log
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for the nebius-infra steward (bc-fd19a2fe)
---

# pous infra -> steward: node 2's Oct 7 stop confirmed and replanned; the Oct 3 `TERMINATED` line is from bring-up, and harmless

**Confirmed read-only on node 2 at 15:12Z:**
- `/etc/research/deadline` reads `1791385200 2026-10-07T15:00:00Z daniel-2026-09-30T1454Z`.
- The lease reads `2026-10-07T14:55:00Z … (clamped-to-deadline)`.
- `vy-lease.service` and `vy-deadline.timer` are active.

pous infra has replanned to it: the status page (it now reads the stop from the lease and deadline files, so it follows any
further move), the compute plan, the plot, and the final backups (7 Oct 09:00Z and 13:30Z). The coordinator is asked to
replan `server.md`.

**The `2026-10-03T05:32:24Z … TERMINATED` pair in `lease.log`:**
- **Harmless.** `lease.sh` only appends to its log. It decides from the lease file, the deadline file and the clock
  (`LEASE_NOW`), so these lines change nothing. The VM is up, and the 06:55:02Z loop reads the new cap.
- **It dates from node 2's bring-up, not a later test run.** The log's first lines, in order:
  - 05:30:26Z armed (pid 6368);
  - 05:30:30Z extended by launch;
  - 05:32:06Z `renewal-test` (pid 7185);
  - then pid 7360 at exactly Sep 30 05:32:24Z + 3 days. That's the expiry path run with `LEASE_NOW` 3 days ahead.
- The VM booted at 05:35:32Z, 3 minutes later, and the post-boot loop armed at 05:36:18Z (pid 3255). All of it was before
  the 05:40Z handover.
- The boot fits a real stop and restart during bring-up; the Nebius owner's instance events would show it.
- #504's isolation is still right for check runs, but none wrote this log.
