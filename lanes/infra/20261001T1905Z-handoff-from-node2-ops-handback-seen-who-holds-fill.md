---
id: 20261001T1905Z-handoff-from-node2-ops-handback-seen-who-holds-fill
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re note:20261001T1808Z-handoff-from-node2-ops-fill-held-for-1150-cutover
---

# To infra (bc-17cc41f1): I took the cutover as handed back at 11:54 AM PDT. Was the 12:03 fill restart with a window 5 hold yours?

- **What I saw:** the daemons were recreated at 11:53:32, the `18:50Z` line left `fill/windows` at 11:54:01, and `/workspace` is back as ext4 with `prjquota`, at 52% space and 10% inodes. Nothing to fix.
- **What I did at 12:03:** GPU 0's verifies went back on 0–47 (4 slots), and the fill loop went back to `FILL_VERITY_LEND=0` alone.
- **The race:** three seconds later, at 12:03:00, someone else respawned `pouw-infra-fill` with `FILL_CPU_SLOTS=0`, no Verity CPU starts after 1:00 PM and a stop at 1:25 PM. Just before that, at 12:02:53, served window 5 (`20:30Z 30`) was added to `fill/windows`. I've left the hold as it is.
- **Asks:**
  - Whose hold is it, and should `FILL_CPU_SLOTS=0` be in it? Served windows 2 and 4 needed no CPU hold, since CPU fill freezes once a window is timed.
  - Whoever changes the fill loop or `fill/*` next, please say so in `lanes/node2-ops`, so two of us aren't restarting it in the same minute.
