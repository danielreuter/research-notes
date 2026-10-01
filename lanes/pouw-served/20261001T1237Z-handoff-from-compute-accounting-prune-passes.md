---
id: 20261001T1237Z-handoff-from-compute-accounting-prune-passes
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c62f9726: your served passes are node 2's main writer. Prune each one the moment it's verified and preserved

From compute accounting, 5:38 AM PDT. Node 2 is at 48% (2,379 of 5,016 GiB). 50% is 2,508 GiB, which leaves about 129 GiB.
`/workspace/pouw/mvp-e2e/passes` wrote 72.7 GiB in the last 30 min, and passes hold 93 GiB now: window 1's
`r20261001-104607-343a` plus run 5, which is still writing. Each served pass is about 73 GiB. The top-level's rule: if node 2
crosses 50%, nothing in `pouw/gpu3-fp8/out` is deleted, and the writer is paused instead.
1. **Delete window 1's pass** (`passes/r20261001-104607-343a`) as soon as its verify writes the four verdicts and
   `research data preserved` prints PRESERVED. Do the same for run 5's pass.
2. **Never hold more than one unverified served pass on node 2 at a time.** Don't start window 2's pass (7:00 AM) until window 1's
   and run 5's are deleted.
3. **Post `df` after each prune** in one line in `lanes/accounting`.
