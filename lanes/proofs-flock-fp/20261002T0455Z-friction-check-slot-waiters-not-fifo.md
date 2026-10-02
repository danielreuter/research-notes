---
id: proofs-flock-fp/20261002T0455Z-friction-check-slot-waiters-not-fifo
lane: proofs-flock-fp
kind: friction
status: open
---

# `check --record --on vy-nebius-1` waits in no order: a later lane check took a slot first

`r20261002-032024-0401` (`check --record` of `85e8434b8`) waited in `tools/check/slot.py` from 03:21Z to about 04:45Z (8:21 to
9:45 PM PDT) with every slot busy. Train checks take freed slots first by design. Meanwhile `r20261002-033938-922f` (launched
03:39Z) and `r20261002-040109-a7ed` (launched 04:01Z) each got a slot before it: every waiter polls `take()` every 20 s, so
the first poll after a release wins, whenever that waiter arrived. In arrival order it would have taken the slot freed at
about 03:41Z, an hour earlier, on a `check` that a PR waits for. A FIFO among `slot.py`'s waiters (a ticket file beside the locks, taken in order) would fix it, or at
least printing the waiter's position would make the wait readable.
