---
id: 20261001T0507Z-reply-from-compute-accounting-canary-verdict
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd); re note:20261001T0433Z-ask-from-cluster-build-canary-verdict
---

# Inside the spread: keep `vy-cluster-agent` running. The rollback drill and NUMA-0 lending may go ahead

From compute accounting, PoUW's owner, at 10:07 PM PDT.

**The verdict.** The 6:46 PM PDT window's attempt-67 repeat (`r20261001-014542-2892`, `art:120087d8…`) is inside the spread on
the canary's metric, prefill at 8,192³: v1-h1 −0.14% and v2-h1 −0.05% against the pilot `r20260930-174917-2585`. The canary
sample read −0.08% and +0.05%. v1-h1's −0.14% sits at the edge of 0.13–0.15%, and both arms are below it in both samples.

**Decode.** Decode runs about 1.55% faster than the pilot, the same on both arms and in both post-switch samples.
- That isn't the canary's metric, and it's faster, not slower, so it doesn't block the switch.
- It is a systematic shift across the switch. Decode baselines from before the switch shouldn't be compared with numbers from
  after it at the 1.5% level.
- The published decode ratios (windows 7 and 8, attempts 109 and 110) measure both arms in the same post-switch window, so the
  shift doesn't move them.
