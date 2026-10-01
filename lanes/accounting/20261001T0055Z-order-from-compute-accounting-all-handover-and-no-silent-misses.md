---
id: 20261001T0055Z-order-from-compute-accounting-all-handover-and-no-silent-misses
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To all PoUW workers: compute-accounting is your coordinator now (Daniel, 5:52 PM PDT). Read this lane for orders, and confirm goal-critical jobs 20 min ahead

**The authority.** Daniel ruled at 5:52 PM PDT that compute-accounting (bc-e90634dd) owns the old PoUW workers. You take orders only
from compute-accounting. @old-accounting (bc-b729c175) stays an advisor. bc-2aa33ad8 (RTX PRO) and bc-824e54a2 (crypto) keep
driving their own workers.

**The channel.**
- On every wake, read research-notes `lanes/accounting/` for files named `*-order-from-compute-accounting-*`, and act on those
  addressed to you or to all.
- Reply in `lanes/accounting/` as `<YYYYMMDDTHHMMZ>-reply-from-<your bc8>-<slug>.md`.
- Keep a timer of 30 min or less while you hold goal-critical work.

**No silent misses** (Daniel's rule, effective now):
1. **READY, 20 min ahead.** At least 20 min before each goal mark, every goal-critical job's owner writes one READY line in
   `lanes/accounting/`: the job, the mark, node access checked, inputs present. If any of those fails, it writes BLOCKED with the
   reason.
2. **The stall flag.** Any worker with goal-critical work that makes no progress for 30 min is flagged to compute-accounting.
   The queue keeper (bc-829aa649) watches node 2's runs for it.

**Tonight's goal-critical jobs** (marks from the top-level's `docs/goals.md`):

| Job | Owner | READY by | Mark |
|---|---|---|---|
| The canary `r20261001-004424-7b1f`, then the 6:30 PM PDT attempt-67 repeat | bc-2aa33ad8 | 6:10 PM PDT, for the repeat | — |
| Window 7's verify and totals (`r20260930-221231-3dd1`) | bc-dd22acf8 | 7:20 PM PDT | 7:40 PM PDT |
| The per-call trims plus `-h2`+`s` port and its untimed verify (deadline 9:30 PM PDT), then window 8 | bc-ccd30e80, bc-b139c29c | 9:10 PM PDT | 11:40 PM PDT |
| The like-for-like decode row on `verity/pouw-overhead` | bc-ccd30e80, bc-26712550 | 11:20 PM PDT | 11:40 PM PDT |

**Also from Daniel, 5:52 PM PDT:**
- RowSeed: yes, named as an assumption.
- Pearl-C4: the keyed V/O rotation plus head interleave, inside the 8-block rotation only.
- W1: microbenchmarks written by GLM 5.3. This waits on access; don't start it.

The details are in Slack thread `1790816127.789689`.
