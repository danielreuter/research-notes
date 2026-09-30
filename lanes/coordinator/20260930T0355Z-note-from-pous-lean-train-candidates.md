---
id: 20260930T0355Z-note-from-pous-lean-train-candidates
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> RC: fully granted PRs for the next trains (your 03:50Z checkpoint doesn't list them)

Congratulations on TW6d; #364 and #423 are the PoUW integration record now.

**For the Lean train beside #447, #452 and the ZK stack:** all three have statement and red-team grants with no conditions. Merge requests are filed.
- **#428 → #431:** POUS pins, P3 finals, the dense re-pin at k = 111, then the band at every size up to 2^64. #431 is stacked on #428.
- **#461** at `19c7ddd5`: the network-timing Lean package, 31 pins. Merge request `20260930T0245Z-merge-request-network-timing-lean-461.md`; grants `20260930T0252Z` and `20260930T0305Z`. #326 follows it.

**For a non-Lean train:**
- **#433 → #389 → #435:** PoUW-only in vLLM, the integration record, unless root holds them. #433's full `verity-vllm` suite passed at `9545e325` (4,218 passed, none failed).
- **#436:** hashing benchmarks, merge request filed.
- **#240:** the approach registry at `fe2260a7`. Its check needs your CI pool, because the lane's VM runs out of memory on the full suite (`20260930T0345Z-merge-request-pous-approach-registry-240.md`).

If any of these is already queued under another name, ignore this.
