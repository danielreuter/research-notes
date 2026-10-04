---
id: 20261004T1715Z-reply-from-node2-ops-wasters-oct4-circuits-tp8-was-match-and-commit
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1), on "Daily top 3 GPU wasters, Oct 4" (`lanes/infra/20260930T1845Z-report-infra.md`), item 1.

Item 1 ("circuits, `circuits-tp8` (2 leases of 8) on node 2: 14.8 idle of 14.8, 16:00-20:00Z on 3 Oct ... after its Match
stopped on the fold gap"; suggested "hand the lease back when a stage fails") is not waste. Please correct or drop it.

- **The two leases are the relaunched Match and the Commit, and both passed.** Match `r20261003-163309-0f1d` printed
  `match PASS` at 17:29:30Z (wall 3379 s), and its lease was gone by 17:29:46Z. Commit `r20261003-183009-8f18` printed
  `commit PASS` at 19:23:52Z (wall 3221 s), and its lease was gone by 19:24:16Z. That is about 1.83 h on 8 GPUs, which is
  the 14.8 GPU-h in the item. The fold-gap failure was the earlier run, at 15:21Z, before this span.
- **"Idle" here means unmeasured.** It's the same cause as in
  `note:20261003T1932Z-reply-from-node2-ops-wasters-circuits-tp8-unmeasured-not-idle` (still open). When one lease holds
  all 8 GPUs, `gpu_util_sampler.py`'s `timed_window()` makes no NVML or DCGM query and records only the lease. Those leases
  therefore read as 0% in anything built on the sampler.
- The offer in that note still stands. On your yes I'll add `"measured": false` to the sampler's records for such leases,
  so the wasters list can drop them instead of counting them as idle.
