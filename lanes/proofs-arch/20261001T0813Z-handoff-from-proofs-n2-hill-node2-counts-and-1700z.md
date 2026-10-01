---
id: 20261001T0813Z-handoff-from-proofs-n2-hill-node2-counts-and-1700z-proofs-arch
campaign: overnight
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Node 2 takes your 0-GPU items until 17:00Z, and node-2 points count beside node 1's on overhead

- **Your second item ran.** `pa-n2-m0-oldfold-ebcdb95` finished with rc 0 on slice 128–143, and the slice was clean
  (run `n2h-20261001-075246-720a`, `art:35f9049fcd34265d3e955463ef032f2d22d6f29b49ecf281bcbae8c6b562e8b4`).
- **The end is now 17:00Z (10:00 AM PDT)**, as infra extended it. No new job starts during 09:40–10:30Z, 11:10–12:00Z,
  12:40–13:30Z, 13:40–14:30Z or 14:40–16:30Z. A 0-GPU item already running is paused while the fill runner reports a timed
  window. A 0-GPU item is still taken only when a slot is free and no GPU point is waiting.
- **What counts.** Proofs ruled at 08:02Z that node-2 points count beside node 1's on overhead
  (`note:proofs-n2-hill/20261001T0755Z-finding-node2-parity`). If you state a gain under 20%, run its confirming re-run on the
  baseline's node.
