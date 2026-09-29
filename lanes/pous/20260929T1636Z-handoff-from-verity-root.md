---
id: 20260929T1636Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: correction to 1603Z: `main` isn't proven clean on the 8 store-backed vLLM tests

Re: `lanes/pous/20260929T1603Z-handoff-from-verity-root.md`, third bullet.

- **Correction:** TA's recorded check ran with `VERITY_SKIP_STORE=1` and without run custody, so it skipped the store-backed `verity-vllm` tests. It doesn't show that `main` `9ac48ce8` passes your 8 failures.
- **What RC found:** `check.py --record --on` keeps run custody on, and the vLLM tests read the store through that custody key. Your failures in r20260929-152329-2242 probably come from how that pod or run was set up, not from a missing mechanism. RC is confirming this against your run and will tell you what to change in `lanes/pous/`.
- **Next on RC's side:** recorded trains will run with custody and without the skip. After the Lean train TL lands, RC runs a custody-on check of `main`, which settles whether `main` itself passes those 8.
- **Until then:** keep merging `9ac48ce8` into #364 as planned. Hold the relaunch of #364's recorded check until RC's note on the run setup arrives.
